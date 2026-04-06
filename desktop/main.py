#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
地球村民监察互助联盟 - Windows 桌面客户端

运行方式：python main.py
打包 exe: pyinstaller --windowed --onefile --icon=app.ico main.py
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QTextEdit, QMessageBox, QFileDialog, QProgressBar,
    QHeaderView, QComboBox, QStatusBar, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon
import json
import requests

# API 配置
API_BASE_URL = "http://127.0.0.1:8000/api"


class APIClient:
    """API 客户端"""

    @staticmethod
    def post(endpoint, data=None):
        url = f"{API_BASE_URL}/{endpoint}"
        response = requests.post(url, json=data)
        return response.json() if response.status_code < 400 else None

    @staticmethod
    def get(endpoint):
        url = f"{API_BASE_URL}/{endpoint}"
        response = requests.get(url)
        return response.json() if response.status_code < 400 else None


class VoteThread(QThread):
    """投票请求线程"""
    result_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, category, company_id, reason):
        super().__init__()
        self.category = category
        self.company_id = company_id
        self.reason = reason

    def run(self):
        try:
            result = APIClient.post(
                "vote/submit/",
                {
                    'category': self.category,
                    'company_id': self.company_id,
                    'reason': self.reason,
                }
            )
            if result:
                self.result_signal.emit(result)
            else:
                self.error_signal.emit("投票失败，请稍后重试")
        except Exception as e:
            self.error_signal.emit(f"网络错误：{str(e)}")


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.user_id = None
        self.username = None
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("地球村民监察互助联盟 - 投票系统")
        self.setMinimumSize(1000, 700)

        # 主部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 顶部标题栏
        title_label = QLabel("🌍 地球村民监察互助联盟")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        subtitle = QLabel("监督企业就业歧视 | 保障劳动者权益 | 实现社会透明化")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)

        # 标签页导航
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, stretch=1)

        # 登录注册页面
        login_widget = self.create_login_tab()
        self.tabs.addTab(login_widget, "🔐 登录/注册")

        # 投票页面
        voting_widget = self.create_voting_tab()
        self.tabs.addTab(voting_widget, "📊 投票榜单")

        # 结果查看页面
        results_widget = self.create_results_tab()
        self.tabs.addTab(results_widget, "📈 排行查询")

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("请连接网络后使用")

    def create_login_tab(self):
        """登录注册标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 登录表单
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)

        username_label = QLabel("手机号:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入 11 位手机号")

        password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("请输入登录密码")

        verify_code_label = QLabel("验证码:")
        self.verify_code_input = QLineEdit()
        self.verify_code_input.setPlaceholderText("6 位数字验证码")

        send_verify_btn = QPushButton("获取验证码")
        send_verify_btn.clicked.connect(self.send_verification)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(verify_code_label)
        verify_hbox = QHBoxLayout()
        verify_hbox.addWidget(self.verify_code_input)
        verify_hbox.addWidget(send_verify_btn)
        form_layout.addLayout(verify_hbox)

        # 登录/注册按钮切换
        self.login_mode = True

        def toggle_mode():
            if self.login_mode:
                login_to_register()
            else:
                register_to_login()

        def login_to_register():
            form_frame.setEnabled(False)
            self.login_btn.setText("已有账号？立即登录")
            self.username_input.setPlaceholderText("确认手机号")
            self.password_input.hide()
            verify_code_label.hide()
            self.verify_code_input.show()
            send_verify_btn.show()
            self.register_btn.setText("返回登录")
            self.login_mode = False

        def register_to_login():
            form_frame.setEnabled(True)
            self.login_btn.setText("立即注册")
            self.username_input.setPlaceholderText("请输入 11 位手机号")
            self.password_input.show()
            verify_code_label.show()
            send_verify_btn.hide()
            self.register_btn.setText("已有账号？立即登录")
            self.verify_code_input.clear()
            self.login_mode = True

        # 按钮布局
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("立即注册")
        self.login_btn.clicked.connect(self.handle_login)

        self.register_btn = QPushButton("返回登录")
        self.register_btn.clicked.connect(register_to_login)
        self.register_btn.setEnabled(False)

        btn_layout.addStretch()
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.register_btn)

        form_layout.addStretch()
        form_layout.addLayout(btn_layout)
        layout.addWidget(form_frame, stretch=1)

        return widget

    def send_verification(self):
        """发送验证码"""
        phone = self.username_input.text().strip()
        if not phone or len(phone) != 11:
            QMessageBox.warning(self, "提示", "请输入有效的 11 位手机号")
            return

        result = APIClient.post("auth/send-verification/", {"phone": phone})
        if result and 'message' in result:
            self.status_bar.showMessage(f"验证码已发送：{result['message']}")
            QMessageBox.information(self, "提示", result['message'])
            QTimer.singleShot(5000, lambda: self.register_btn.setEnabled(True))
        else:
            QMessageBox.warning(self, "错误", "发送失败，请稍后重试")

    def handle_login(self):
        """处理登录/注册"""
        if not self.login_mode:
            # 注册流程
            phone = self.username_input.text().strip()
            password = self.password_input.text().strip()
            code = self.verify_code_input.text().strip()

            if len(phone) != 11 or len(password) < 6 or len(code) != 6:
                QMessageBox.warning(self, "提示", "请填写完整信息")
                return

            result = APIClient.post("auth/register/", {
                "phone": phone,
                "password": password,
                "code": code,
            })

            if result and 'message' in result:
                QMessageBox.information(self, "成功", f"{result['message']}")
                self.login_btn.setText("立即登录")
                QTimer.singleShot(5000, lambda: self.register_btn.setText("返回登录"))
                QTimer.singleShot(6000, lambda: self.tabs.setCurrentIndex(1))
            else:
                QMessageBox.warning(self, "错误", result.get('error', '注册失败'))

    def create_voting_tab(self):
        """投票标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 榜单选择
        category_layout = QHBoxLayout()
        category_label = QLabel("选择榜单:")
        self.category_combo = QComboBox()

        from apps.voting.models import VoteCategory
        for value, label in VoteCategory.choices:
            self.category_combo.addItem(label, value)

        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)

        # 企业名称搜索
        search_layout = QHBoxLayout()
        company_label = QLabel("目标企业:")
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("输入企业名称或关键词搜索")
        self.company_search_btn = QPushButton("搜索企业")
        self.company_search_btn.clicked.connect(self.search_companies)

        search_layout.addWidget(company_label)
        search_layout.addWidget(self.company_input, stretch=1)
        search_layout.addWidget(self.company_search_btn)
        layout.addLayout(search_layout)

        # 搜索结果列表
        self.company_table = QTableWidget()
        self.company_table.setColumnCount(4)
        self.company_table.setHorizontalHeaderLabels(["ID", "企业名称", "行业", "城市"])
        self.company_table.selectionModel().selectionChanged.connect(self.on_company_selected)
        layout.addWidget(self.company_table, stretch=1)

        # 投票理由文本框
        reason_label = QLabel("投票理由（详细描述歧视或剥削行为）:")
        self.reason_textedit = QTextEdit()
        self.reason_textedit.setPlaceholderText("请详细说明您在该企业遭遇的就业歧视、职场 PUA 或过劳剥削等情况...\n支持文字描述，建议附上证据截图")
        layout.addWidget(reason_label)
        layout.addWidget(self.reason_textedit, stretch=1)

        # 投票按钮
        self.submit_vote_btn = QPushButton("📤 提交投票 (需要上传证据)")
        self.submit_vote_btn.setEnabled(False)
        self.submit_vote_btn.clicked.connect(self.submit_vote)
        layout.addWidget(self.submit_vote_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return widget

    def search_companies(self):
        """搜索企业"""
        query = self.company_input.text().strip()
        if not query:
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return

        # API endpoint: /api/vote/companies/search/
        result = APIClient.get(f"vote/companies/search/?q={query}")
        if isinstance(result, list):
            self.company_table.setRowCount(len(result))
            for row, company in enumerate(result):
                self.company_table.setItem(row, 0, QTableWidgetItem(str(company['id'])))
                self.company_table.setItem(row, 1, QTableWidgetItem(company['name']))
                self.company_table.setItem(row, 2, QTableWidgetItem(company['industry']))
                self.company_table.setItem(row, 3, QTableWidgetItem(company['city']))
        else:
            QMessageBox.warning(self, "提示", f"搜索失败：{result}")

    def on_company_selected(self):
        """企业被选中"""
        selected = self.company_table.selectionModel().selectedRows()
        if selected:
            self.submit_vote_btn.setEnabled(True)

    def submit_vote(self):
        """提交投票"""
        company_id = self.company_table.item(
            self.company_table.currentRow(), 0
        ).text()
        category = self.category_combo.currentData()
        reason = self.reason_textedit.toPlainText().strip()

        if not reason or len(reason) < 10:
            QMessageBox.warning(self, "提示", "投票理由不少于 10 个字")
            return

        # 确认提交
        reply = QMessageBox.question(
            self, '确认提交',
            f'确定要向"{self.company_input.text()}"提交投票吗？\n这将记录您的设备信息和 IP。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # 显示进度条
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)
        progress_bar.setFormat("提交中...")
        self.status_bar.addPermanentWidget(progress_bar)

        self.vote_thread = VoteThread(category, company_id, reason)
        self.vote_thread.result_signal.connect(self.on_vote_success)
        self.vote_thread.error_signal.connect(lambda msg: self.on_vote_error(msg))
        self.vote_thread.start()

    def on_vote_success(self, result):
        """投票成功"""
        QMessageBox.information(
            self, "成功",
            f"投票已提交！\n剩余今日票数：{result.get('remaining_today', 'N/A')}"
        )
        self.submit_vote_btn.setEnabled(False)

    def on_vote_error(self, msg):
        """投票失败"""
        QMessageBox.warning(self, "错误", msg)

    def create_results_tab(self):
        """排行查询标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 榜单选择
        category_label = QLabel("选择榜单类型:")
        self.results_category_combo = QComboBox()

        from apps.voting.models import VoteCategory
        for value, label in VoteCategory.choices:
            self.results_category_combo.addItem(label, value)

        layout.addWidget(category_label)
        layout.addWidget(self.results_category_combo)

        # 查询按钮
        query_btn = QPushButton("🔍 查询排行")
        query_btn.clicked.connect(self.query_ranking)
        layout.addWidget(query_btn)

        # 排行榜表格
        self.rankings_table = QTableWidget()
        self.rankings_table.setColumnCount(5)
        self.rankings_table.setHorizontalHeaderLabels(["排名", "企业名称", "行业", "城市", "投票率"])
        layout.addWidget(self.rankings_table, stretch=1)

        return widget

    def query_ranking(self):
        """查询特定榜单排行"""
        category = self.results_category_combo.currentData()
        result = APIClient.get(f"vote/ranking/{category}/")

        if isinstance(result, dict) and 'rankings' in result:
            rankings = result['rankings']
            self.rankings_table.setRowCount(len(rankings))
            for row, rank in enumerate(rankings):
                self.rankings_table.setItem(row, 0, QTableWidgetItem(f"{rank['rank']}"))
                self.rankings_table.setItem(row, 1, QTableWidgetItem(rank['company_name']))
                self.rankings_table.setItem(row, 2, QTableWidgetItem(rank['industry']))
                self.rankings_table.setItem(row, 3, QTableWidgetItem(rank['city']))
                self.rankings_table.setItem(row, 4, QTableWidgetItem(f"{rank['vote_rate']:.2f}%"))
        else:
            QMessageBox.warning(self, "错误", f"查询失败：{result}")

    def on_vote_success(self, result):
        """投票成功"""
        QMessageBox.information(
            self, "成功",
            f"投票已提交！\n剩余今日票数：{result.get('remaining_today', 'N/A')}"
        )
        self.submit_vote_btn.setEnabled(False)

    def on_vote_error(self, msg):
        """投票失败"""
        QMessageBox.warning(self, "错误", msg)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

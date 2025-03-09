import sqlite3
import tkinter as tk
from tkinter import messagebox
from database import init_database, add_issue, get_issues  # add_issue 임포트 확인
import smtplib
from email.mime.text import MIMEText
import config

# 데이터베이스 파일 경로 설정
db_path = 'issues.db'

# 데이터베이스 초기화 함수 호출
init_database(db_path)

# 팀원 정보
team_members = {
    'John Doe': 'john.doe@example.com',
    'Jane Smith': 'jane.smith@example.com'
}

class MainWindow:
    def __init__(self, root, db_path):
        self.root = root
        self.db_path = db_path
        self.root.title('Issue Tracker')
        self.root.geometry('600x400')  # 창 크기 설정

        # 이슈 목록 표시를 위한 리스트박스
        self.issue_listbox = tk.Listbox(root, height=15, width=80)
        self.issue_listbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.issue_ids = []

        # 버튼 추가
        create_button = tk.Button(root, text='Create New Issue', command=self.create_new_issue_window)
        create_button.grid(row=1, column=0, padx=10, pady=5)
        refresh_button = tk.Button(root, text='Refresh', command=self.populate_listbox)
        refresh_button.grid(row=1, column=1, padx=10, pady=5)

        self.populate_listbox()

    def populate_listbox(self):
        issues = get_issues(self.db_path)  # 데이터베이스에서 이슈 목록 가져오기
        self.issue_listbox.delete(0, tk.END)
        self.issue_ids.clear()
        for issue in issues:
            issue_id, title, _, _, _, _, _ = issue
            self.issue_listbox.insert(tk.END, f"ID: {issue_id} | {title}")
            self.issue_ids.append(issue_id)

    def create_new_issue_window(self):
        new_window = tk.Toplevel(self.root)
        new_window.title('Create New Issue')
        new_window.geometry('400x300')  # 창 크기 설정

        tk.Label(new_window, text='Title:').grid(row=0, column=0, padx=10, pady=5)
        title_entry = tk.Entry(new_window, width=40)
        title_entry.grid(row=0, column=1, padx=10, pady=5)
        new_window.title_entry = title_entry

        tk.Label(new_window, text='Description:').grid(row=1, column=0, padx=10, pady=5)
        description_text = tk.Text(new_window, height=5, width=30)
        description_text.grid(row=1, column=1, padx=10, pady=5)
        new_window.description_text = description_text

        tk.Label(new_window, text='Assignee:').grid(row=2, column=0, padx=10, pady=5)
        assignee_var = tk.StringVar(new_window)
        assignee_var.set('')  # 기본값 설정
        assignee_options = list(team_members.keys())
        assignee_dropdown = tk.OptionMenu(new_window, assignee_var, *assignee_options)
        assignee_dropdown.grid(row=2, column=1, padx=10, pady=5)
        new_window.assignee_var = assignee_var

        tk.Label(new_window, text='Status:').grid(row=3, column=0, padx=10, pady=5)
        status_var = tk.StringVar(new_window)
        status_var.set('Open')  # 기본값 설정
        status_options = ['Open', 'In Progress', 'Closed']
        status_dropdown = tk.OptionMenu(new_window, status_var, *status_options)
        status_dropdown.grid(row=3, column=1, padx=10, pady=5)
        new_window.status_var = status_var

        submit_button = tk.Button(new_window, text='Submit', command=lambda: self.submit_new_issue(new_window))
        submit_button.grid(row=4, column=0, columnspan=2, pady=10)

    def submit_new_issue(self, new_window):
        title = new_window.title_entry.get()
        description = new_window.description_text.get("1.0", tk.END).strip()
        assignee = new_window.assignee_var.get()
        status = new_window.status_var.get()

        if not title or not assignee or not status:
            messagebox.showwarning('Warning', 'Please fill in all fields.')
            return

        # database.py에서 임포트한 add_issue 함수를 직접 호출
        issue_id = add_issue(title, description, assignee, status, self.db_path)
        self.notify_assignee(issue_id, assignee)  # 이메일 알림 전송
        self.populate_listbox()
        new_window.destroy()
        messagebox.showinfo('Info', f'Issue {issue_id} created successfully.')

    def notify_assignee(self, issue_id, assignee):
        if assignee not in team_members:
            messagebox.showwarning('Warning', f'Assignee {assignee} not found in team members list. No email sent.')
            return

        to_email = team_members[assignee]
        issue = self.get_issue_by_id(issue_id)
        if not issue:
            messagebox.showerror('Error', f'Issue {issue_id} not found. No email sent.')
            return

        title = issue[1]  # title은 두 번째 필드
        description = issue[2]  # description은 세 번째 필드
        body = f'New issue assigned to you:\n\nTitle: {title}\nDescription: {description}\n\nPlease check the issue tracker for more details.'

        try:
            self.send_email('New Issue Assigned', body, to_email)
            messagebox.showinfo('Info', f'Email sent to {assignee} ({to_email}).')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to send email: {str(e)}')

    def get_issue_by_id(self, issue_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM issues WHERE id = ?', (issue_id,))
        issue = cursor.fetchone()
        conn.close()
        return issue

    def send_email(self, subject, body, to_email):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = config.EMAIL_FROM
        msg['To'] = to_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(config.EMAIL_FROM, config.EMAIL_PASSWORD)
        server.sendmail(config.EMAIL_FROM, to_email, msg.as_string())
        server.quit()

if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindow(root, db_path)
    root.mainloop()
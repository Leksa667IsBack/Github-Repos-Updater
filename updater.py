import tkinter as tk
import requests
import base64
import time
from threading import Thread
import sys

class GitHubUpdaterApp:
    def __init__(self, master):
        self.master = master
        master.title("GitHub Updater")
        master.geometry("867x250")
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.label = tk.Label(master, text="GitHub Updater", font=("Helvetica", 20))
        self.label.pack(pady=10)

        self.status_label = tk.Label(master, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        self.update_button = tk.Button(master, text="Start Updating", command=self.start_update, font=("Helvetica", 12))
        self.update_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop Updating", command=self.stop_update, state=tk.DISABLED, font=("Helvetica", 12))
        self.stop_button.pack(pady=10)

        sys.stdout = open("NUL", "w")
        sys.stderr = open("NUL", "w")

        self.github_token = "YOUR_GITHUB_TOKEN_HERE"
        self.repo_info = [
            {"owner": "Owner1", "repo_name": "Repo1"},
            {"owner": "Owner2", "repo_name": "Repo2"},
            {"owner": "Owner3", "repo_name": "Repo3"}
        ]

        self.updating = False

    def start_update(self):
        self.updating = True
        self.update_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_status("Updating...")

        update_thread = Thread(target=self.update_loop)
        update_thread.start()

    def stop_update(self):
        self.updating = False
        self.update_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("Update stopped.")

    def update_status(self, message):
        self.status_label.config(text=message)

    def get_current_readme(self, owner, repo):
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            readme_content = response.json()
            decoded_content = base64.b64decode(readme_content['content']).decode('utf-8')
            return decoded_content
        else:
            print(f"Failed to fetch README.md from {owner}/{repo}: {response.text}")
            return None

    def update_readme(self, owner, repo, content):
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            readme_content = response.json()
            sha = readme_content['sha']
            update_data = {
                "message": "Update README.md",
                "content": base64.b64encode(content.encode()).decode(),  # Encode the content in Base64
                "sha": sha
            }
            update_response = requests.put(url, headers=headers, json=update_data)
            if update_response.status_code == 200:
                print(f"README.md updated successfully in {owner}/{repo}.")
                self.update_status(f"README.md updated successfully in {owner}/{repo}.")
            else:
                print(f"Failed to update README.md in {owner}/{repo}: {update_response.text}")
                self.update_status(f"Failed to update README.md in {owner}/{repo}.")
        else:
            print(f"Failed to fetch README.md from {owner}/{repo}: {response.text}")
            self.update_status(f"Failed to fetch README.md from {owner}/{repo}.")

    def update_loop(self):
        while self.updating:
            for repo in self.repo_info:
                current_readme = self.get_current_readme(repo['owner'], repo['repo_name'])
                if current_readme is not None:
                    self.update_readme(repo['owner'], repo['repo_name'], current_readme)
            time.sleep(11)  # Sleep for 11 seconds

    def on_close(self):
        self.updating = False
        self.master.destroy()

def main():
    root = tk.Tk()
    app = GitHubUpdaterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

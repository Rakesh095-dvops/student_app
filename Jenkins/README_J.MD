## Pre-Requisites

- **EC2 Setup:**  
  Set up two EC2 instances: one for staging and one for production. Ensure port `5000` is open to `0.0.0.0`.
  
  ![EC2 Setup](1-AWS_screenshot.png)

- **Jenkinsfile:**  
  The `Jenkinsfile` contains all pipeline stages and steps.  
  - Ensure the `environment` block is filled with all required details for the pipeline and Flask app, such as **AWS SSH Credentials** and **Docker Hub Credentials**.

- **Email Notification Configuration:**  
  1. **Install Plugins:**
      - Email Extension Plugin
      - Email Extension Template Plugin
      - Pipeline: GitHub (for commit tracking)
  2. **Configure System Settings:**
      - Go to: `Manage Jenkins → Configure System → Email Notification`
      - SMTP server: `smtp.gmail.com`
      - SMTP Port: `587`
      - Use SSL: ✔️
      - Use TLS: ✔️
      - Credentials: Add your email/password

    ```bash
    # Example: Email Notification Settings
    SMTP server: smtp.gmail.com
    SMTP Port: 587
    Use SSL: true
    Use TLS: true
    Credentials: <your-email-credentials>
    ```

---

## Jenkins CI/CD in Action

- **Automatic build** is triggered based on SCM polling.
- **Build Success:**
  ![Build Success](0-Build_screenshot.png)
- **Email Notifications:**  
  Emails are sent to intended recipients.
  ![Email Success](Sucess_build.png)
- **Docker Repository:**  
  Latest build is pushed.
  ![Docker Push](5-Docker_push.png)
- **Staging Environment:**  
  Up and running.
  ![Staging](3-PRE_PROD.png)
- **Production Environment:**  
  Up and running.
  ![Production](2-PROD_a.png)
  ![Production Health](4-PROD-Health.png)

---

### **Note**

- Simulate builds for `abort` and `failed` scenarios to verify email notifications:
    - **Abort:**  
      ![Abort Build](abort_build.png)
    - **Failed:**  
      ![Failed Build](Failed_build.png)
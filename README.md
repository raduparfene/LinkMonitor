# 🔗💻 LinkMonitor
- Smart web monitoring system on a budget
- It monitors web pages, notifying through emails any content change 

## 🛠️ Setup & Prerequisites
### 🐍💻 Python Application
Create an ```.env``` file with the following content:
```bash
LM_SMTP_HOST=smtp.gmail.com
LM_SMTP_PORT=587
LM_SMTP_EMAIL=you@gmail.com
LM_SMTP_PASSWORD=YOUR_APP_PASSWORD # e.g. App password key
LM_TO=you@gmail.com,other@domain.com
LM_REQUESTS_CA_BUNDLE=./certs/cacert.pem # you have to use the certificate provided by the page you monitor
LM_PROFILE=news # you can monitor different types of links: links_example.txt, links_news.txt
```
- after this, create the link files inside ```links``` directory, following the ```links_example.txt``` tuple structure, where ```example``` will be the profile you use for the ```LM_PROFILE``` property
- run the ```link_monitor.py``` script
- More info inside: ```/docs/application```  
-----------------

## 📈 Monitoring Logic
1. **Fetch**: Download the page content
2. **Compare**: Verify the differences
3. **Notify**: If there are differences, send and email with screenshots via Playwright (assuming it was installed)
4. **Cleanup**: The cronjob Alpha stops the EC2 instance to save money and resources


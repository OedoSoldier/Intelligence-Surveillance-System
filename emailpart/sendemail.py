import smtplib
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.login("youremailaccount", "password")
 
msg = "YOUR MESSAGE!"
server.sendmail("youremailaccount", "receiveraddress", msg)
server.quit()

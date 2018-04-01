import smtplib
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.login("wenganq11@gmail.com", "Realme320!")
 
msg = "YOUR MESSAGE!"
server.sendmail("wenganq11@gmail.com", "wengq@bu.edu", msg)
server.quit()
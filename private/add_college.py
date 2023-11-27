#!/usr/bin/env python3
import sqlite3
from random import randint
from sys import argv
import bcrypt

DB_PATH = "heel.db"

if len(argv) == 4:
  collegename, collegecontact, collegediscord = argv[1:4]
  collegepass = input("Enter College password: ")
  collegepassconf = input("Confirm College password: ")
else:
  collegename = input("Enter College name: ")
  collegepass = input("Enter College password: ")
  collegepassconf = input("Confirm College password: ")
  collegecontact = input("Enter College contact: ")
  collegediscord = input("Enter College discord: ")

if collegepass == collegepassconf:
  conn = sqlite3.connect(DB_PATH)
  command = conn.cursor()

  collegeid = str(randint(1, 99999)).zfill(5)  # I hope there are no clashes
  salt = bcrypt.gensalt()
  hashedpw = bcrypt.hashpw(collegepass.encode("utf-8"), salt)

  adddetails = "INSERT INTO Colleges (CollegeID, CollegePassword, CollegeName, CollegeContact, CollegeDiscord) VALUES (?,?,?,?,?)"
  print([collegeid, collegepass, collegename, collegecontact, collegediscord])
  command.execute(
    adddetails,
    [collegeid, hashedpw, collegename, collegecontact, collegediscord])
  conn.commit()
  conn.close()
else:
  print("Passwords not the same, database not updated.")

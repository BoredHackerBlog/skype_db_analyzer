import sqlite3
import sys
from prettytable import PrettyTable
from datetime import datetime
from pprint import pprint
import collections

if len(sys.argv) < 2:
    print "Usage: " + sys.argv[0] + " main.db"
    quit()

conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

#Information about the main account
account = c.execute("select signin_name, skypename, fullname, birthday, country, province, city, phone_home, phone_office, phone_mobile, emails, mood_text, mood_timestamp from Accounts").fetchall()[0]

signin_name = str(account[0])
skypename = str(account[1])
fullname = str(account[2])
if account[3]:
        birthday = datetime.fromtimestamp(account[3])
else:
        birthday = ""
location = str(account[4]) + " " + str(account[5]) + " " + str(account[6])
phone_numbers = str(account[7]) + " " + str(account[8]) + " " + str(account[9])
emails = str(account[10])
mood = str(datetime.fromtimestamp(account[12])) + " " + account[11]

print "="*25
print "User Information"
print "-"*25
account_t = PrettyTable(["Signin Name",signin_name])
account_t.add_row(["Skype Name: " , skypename])
account_t.add_row(["Full Name: " , fullname])
account_t.add_row(["Birthday: " , birthday])
account_t.add_row(["Location: " , location])
account_t.add_row(["Phone Numbers: " , phone_numbers])
account_t.add_row(["Emails: " , emails])
account_t.add_row(["Mood: " , mood])
print account_t
print "="*25

#Information about contacts
#includes people who are not in contact list but were in group chat
contacts = c.execute("select skypename, fullname, displayname, birthday, country, province, city, phone_home, phone_office, phone_mobile, emails, isblocked, mood_text from contacts").fetchall()
number_of_contacts = str(len(contacts))

print "="*25
print "Contact Information"
print "This includes people in group chats, main user, and spammers..."
print "-"*25
print "Number of contacts: " + number_of_contacts
contacts_t = PrettyTable(["Skype Name", "Display Name", "Birthday", "Country", "Province", "City", "Phone - Home", "Phone - Office", "Phone - Mobile", "Emails", "Blocked?", "Mood Text"])
for contact in contacts:
    if contact[3]:
            contact_birthday = datetime.fromtimestamp(contact[3])
    else:
            contact_birthday = ""
    contacts_t.add_row([contact[0], contact[2], contact_birthday, contact[4], contact[5], contact[6], contact[7], contact[8], contact[9], contact[10], contact[11], contact[12]])
print contacts_t
print "="*25

message_stats = c.execute("select distinct author, count(*) from messages group by author order by count(*) desc").fetchall()

print "="*25
print "Message Statistics"
print "Includes file transfers, links, and etc."
print "-"*25
message_stats_t = PrettyTable(["Author","# of Messages"])
for author in message_stats:
    message_stats_t.add_row([author[0], author[1]])
print message_stats_t
print "="*25

author_hours = {}
message_hours = c.execute("select author, timestamp from messages").fetchall()

for message in message_hours:
    if str(message[0]) is not '':
        if str(message[0]) not in author_hours:
            author_hours[str(message[0])] = {}
        if datetime.fromtimestamp(message[1]).hour in author_hours[str(message[0])]:
            author_hours[str(message[0])][datetime.fromtimestamp(message[1]).hour] += 1
        else:
            author_hours[str(message[0])][datetime.fromtimestamp(message[1]).hour] = 1
    else:
        continue


print "="*25
print "Message Hours"
print "Hour: # of messages"
for authorname in author_hours:
    print "-"*25
    print authorname
    print "-"*25
    pprint(author_hours[authorname])
print "="*25


author_topwords = {}
message_body = c.execute("select author, body_xml from messages").fetchall()

for message in message_body:
    if str(message[0]) is not '':
        if str(message[0]) not in author_topwords:
            author_topwords[str(message[0])] = ""
        else:
            if message[1] is not None:
                body = message[1].encode('ascii','ignore')
                author_topwords[str(message[0])] += " " + body

def top10_words(text):
    counts = collections.Counter(text.split())
    return counts.most_common(10)

print "="*25
print "Top 10 words"
print "Word: # of uses"
for authorname in author_topwords:
    print "-"*25
    print authorname
    print "-"*25
    pprint(top10_words(author_topwords[authorname]))
print "="*25

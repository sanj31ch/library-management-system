import flask as fk
import mysql.connector as mc
from  database import con, cur, cur2
import datetime as dt


libfile=fk.Blueprint('libfile', __name__)

@libfile.route('/deletebook/<int:id>', methods=['DELETE'])
def delbook(id):
   cur.execute("DELETE FROM BOOKS WHERE BOOK_ID = %s", (id,))
   if cur.rowcount==1:
      con.commit()
      return fk.jsonify("Book deleted successfully"), 200
   else:
      return fk.jsonify("Book not found"), 404

@libfile.route('/addsubscription')
def addsub():
    return fk.render_template('addsubscription.html')

@libfile.route('/libhistorydata',methods=['GET'])
def libhistorydata():
   cur2.execute("SELECT * FROM BOOKHISTORY")
   books=cur2.fetchall()
   for book in books:
      book['ISSUE_DATE'] = book['ISSUE_DATE'].isoformat() if book['ISSUE_DATE'] else None
      book['DUE_DATE'] = book['DUE_DATE'].isoformat() if book['DUE_DATE'] else None
      book['RETURN_DATE'] = book['RETURN_DATE'].isoformat() if book['RETURN_DATE'] else None
   if books:
      return fk.jsonify(books), 200
   else:
      return fk.jsonify("No history found"), 404

@libfile.route('/regstudents',methods=['GET'])
def lodstud():
   cur2.execute("SELECT * FROM STUDENT")
   student=cur2.fetchall()
   if student:
         return fk.jsonify(student), 200
   else:
      return fk.jsonify('No registered studentts'),404

@libfile.route('/libdel/<int:sid>',methods=['DELETE'])
def libdel(sid):
   cur.execute("DELETE FROM STUDENT WHERE STUDENT_ID=%s",(sid,))
   if cur.rowcount==1:
      con.commit()
      return fk.jsonify("Deleted"),200
   else:
      return fk.jsonify("Student not found"),404

@libfile.route('/addBook',methods=['POST'])
def addB():
   adet=fk.request.get_json()
   bname=adet.get('name')
   bauthor=adet.get('author')
   bpublish=adet.get('publisher')
   byear=adet.get('year')
   bisbn=adet.get('ISBN')
   bcategory=adet.get('category')
   bdescription=adet.get('des')
   pages=adet.get('pages')
   quantity=adet.get('quantity')
   language=adet.get('lang')
   cur.execute("SELECT MAX(BOOK_ID) FROM BOOKS")
   id=cur.fetchone()[0]
   id=id+1 if id is not None else 1  
   cur.execute("INSERT INTO BOOKS(BOOK_ID,TITLE, AUTHOR, PUBLISHER, YEAR, ISBN, CATEGORY, BDESCRIPTION, PAGES, BLANGUAGE, AVAILABLE, OUT_OF,STATUS) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'AVAILABLE')",(id,bname, bauthor, bpublish, byear, bisbn, bcategory, bdescription, pages, language, quantity, quantity))
   if cur.rowcount==1:
      con.commit()
      return fk.jsonify("Book added successfully"), 201
   else:
      return fk.jsonify("Failed to add book"), 500

@libfile.route('/registerstudent',methods=['POST'])
def adds():
   adet=fk.request.get_json()
   sname=adet.get('name')
   susername=adet.get('user')
   spassword=adet.get('pass')
   semail=adet.get('email')
   scourse=adet.get('course')
   ssem=adet.get('sem')
   smobile=adet.get('mobile')
   sgender=adet.get('gender')
   id=adet.get('enroll')
   cur.execute("INSERT INTO STUDENT(STUDENT_ID,USERNAME,PASSWORD,NAME,COURSE,SEMESTER,EMAIL,MOBILE_NO,BOOKS_ISSUED,GENDER) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0,%s)",(id,susername,spassword,sname,scourse,ssem,semail,smobile,sgender))
   if cur.rowcount==1:
      con.commit()
      return fk.jsonify(f"{sname} registered successfully!"), 201
   else: 
      return fk.jsonify("Failed to register student!"), 500
   
@libfile.route('/issue_book', methods=['POST'])
def issue_book():
    data = fk.request.get_json()
    book_id = data.get('bookId')
    student_id = data.get('studentId')
    request_date = data.get('issueDate')
    due_date = data.get('dueDate')
    notes = data.get('notes')
    cur.execute("SELECT TITLE, PUBLISHER,AVAILABLE,OUT_OF FROM BOOKS WHERE BOOK_ID=%s", (book_id,))
    book = cur.fetchone()
    if not book:
        return fk.jsonify({'error': 'Book not found'}), 404
    if book[2]==0:
        return fk.jsonify({'error':'No available Books for this title'})
    cur.execute("SELECT NAME FROM STUDENT WHERE STUDENT_ID=%s", (student_id,))
    student = cur.fetchone()

    if not student:
        return fk.jsonify({'error': 'Student not found'}), 404

    cur.execute("""
        INSERT INTO BOOK_REQUESTS 
        (BOOK_ID, STUDENT_ID, REQUEST_DATE, STATUS, TITLE, PUBLISHER, STUDENT_NAME,DUE_DATE,NOTES) 
        VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)
    """, (book_id, student_id, request_date, 'PENDING', book[0], book[1], student[0],due_date,notes))

    if cur.rowcount == 1:
        cur.execute("UPDATE BOOKS SET STATUS='REQUESTED' WHERE BOOK_ID=%s", (book_id,))
        con.commit()
        return fk.jsonify({'status': 'success'})
    else:
        return fk.jsonify({'error': 'Failed to insert request'}), 500
    
def get_book_title(book_id):
    cur.execute("SELECT TITLE FROM BOOKS WHERE BOOK_ID=%s", (book_id,))
    result = cur.fetchone()
    return result[0] if result else "Unknown"

def get_student_name(student_id):
    cur.execute("SELECT NAME FROM STUDENT WHERE STUDENT_ID=%s", (student_id,))
    result = cur.fetchone()
    return result[0] if result else "Unknown"

def calculate_overdue_days(due_date, return_date):
    due = dt.datetime.strptime(str(due_date), "%Y-%m-%d")
    ret = dt.datetime.strptime(str(return_date), "%Y-%m-%d")
    delta = (ret - due).days
    return max(0, delta)


@libfile.route('/return_book', methods=['POST'])
def return_book():
    data = fk.request.get_json()
    issue_id = data.get('issueId')
    return_date = data.get('returnDate')
    fine = data.get('fine')
    cur.execute('SELECT CURDATE()')
    today=cur.fetchone()
    # Fetch existing issue details
    cur2.execute("SELECT * FROM BOOK_ISSUES WHERE ISSUE_ID=%s", (issue_id,))
    issue = cur2.fetchone()

    if not issue:
        return fk.jsonify({'status': 'error', 'message': 'Issue not found'}), 404
    cur.execute("SELECT AVAILABLE,OUT_OF FROM BOOKS WHERE BOOK_ID=%s",(issue['BOOK_ID'],))
    aval=cur.fetchone()
    if aval[0]==aval[1]:
        one=0
    else:
        one=1
    fine=str(fine)
    print(type(fine))
    #cur.execute("INSERT INTO BOOKHISTORY VALUES(%s,%s,%s,%s,%s,%s,%s,CURDATE(),%s,%s,'RETURNED','RETURNED BOOK')",(issue_id,issue['BOOK_ID'],get_book_title(issue['BOOK_ID']),issue['STUDENT_ID'],get_student_name(issue['STUDENT_ID']),issue['ISSUE_DATE'],issue['RETURN_DATE'],calculate_overdue_days(issue['RETURN_DATE'],today[0]),fine))
    cur.execute("UPDATE BOOKS SET STATUS='AVAILABLE',AVAILABLE=AVAILABLE+%s WHERE BOOK_ID=%s",(one,issue['BOOK_ID']))
    cur.execute("UPDATE STUDENT SET BOOKS_ISSUED=BOOKS_ISSUED-1 WHERE STUDENT_ID=%s",(issue['STUDENT_ID'],))
    cur.execute("UPDATE BOOK_ISSUES SET ACTUAL_RETURN_DATE=%s, STATUS='Returned' WHERE ISSUE_ID=%s", (return_date, issue_id))
    con.commit()
    return fk.jsonify({'status': 'success'})

@libfile.route('/get_issued_books', methods=['GET'])
def get_issued_books():
    query = """
        SELECT BI.ISSUE_ID, BI.BOOK_ID, B.TITLE AS BOOK_TITLE, 
               BI.STUDENT_ID, S.NAME AS STUDENT_NAME, 
               BI.ISSUE_DATE, BI.RETURN_DATE, BI.ACTUAL_RETURN_DATE, BI.STATUS,F.FINE_AMOUNT AS FINE,F.FINE_ID
        FROM BOOK_ISSUES BI
        JOIN BOOKS B ON BI.BOOK_ID = B.BOOK_ID
        JOIN STUDENT S ON BI.STUDENT_ID = S.STUDENT_ID
         LEFT JOIN FINE F ON BI.ISSUE_ID = F.ISSUE_ID
        
    """
    cur2.execute(query)
    issues = cur2.fetchall()

    for i in issues:
        for key in ['ISSUE_DATE', 'RETURN_DATE', 'ACTUAL_RETURN_DATE']:
            if i.get(key):
                i[key] = i[key].isoformat()
    cur2.execute("SELECT * FROM BOOK_ISSUES WHERE STATUS='Issued'")
    issued_books = cur2.fetchall()
    for book in issued_books:
        if book['RETURN_DATE']< dt.datetime.now().date():
            cur2.execute("UPDATE BOOK_ISSUES SET STATUS='Overdue' WHERE ISSUE_ID=%s", (book['ISSUE_ID'],))
            con.commit()
    return fk.jsonify(issues), 200

@libfile.route('/fines', methods=['GET'])
def get_fines():
    cur2.execute("""
        SELECT F.FINE_ID, F.STUDENT_ID, S.NAME AS NAME, F.SNAME, F.BOOK_ID, 
               F.ISSUE_ID, F.DUE_DATE, F.RETURN_DATE, F.REASON, 
               F.FINE_AMOUNT, F.PAID, B.TITLE AS BOOK_NAME
        FROM FINE F
        JOIN STUDENT S ON F.STUDENT_ID = S.STUDENT_ID
        JOIN BOOKS B ON F.BOOK_ID = B.BOOK_ID
                 
    """)
    fines = cur2.fetchall()
    for f in fines:
        # Convert date objects to ISO format for JSON
        f['DUE_DATE'] = f['DUE_DATE'].isoformat() if f['DUE_DATE'] else None
        f['RETURN_DATE'] = f['RETURN_DATE'].isoformat() if f['RETURN_DATE'] else None
        f['finePaid'] = bool(f['PAID'])  # for frontend display
    return fk.jsonify(fines), 200

@libfile.route('/bookrequests', methods=['GET'])
def lodreq():
    cur2.execute("SELECT * FROM BOOK_REQUESTS WHERE REQUEST_ID IS NOT NULL ORDER BY REQUEST_ID DESC")
    book_requests = cur2.fetchall()
    for req in book_requests:
        req['REQUEST_DATE'] = req['REQUEST_DATE'].isoformat() if req['REQUEST_DATE'] else None
    if book_requests:
        return fk.jsonify(book_requests)
    else:
        return fk.jsonify("No book requests")
    
@libfile.route('/approve_request', methods=['POST'])
def approve_request():
    data = fk.request.get_json()
    request_id = data.get('requestId')
    
    # Fetch the request details
    cur2.execute("SELECT * FROM BOOK_REQUESTS WHERE REQUEST_ID=%s", (request_id,))
    request = cur2.fetchone()
    
    if not request:
        return fk.jsonify({'error': 'Request not found'}), 404
    cur.execute("SELECT AVAILABLE,OUT_OF FROM BOOKS WHERE BOOK_ID=%s",(request['BOOK_ID'],))
    aval=cur.fetchone()
    if aval[0]==0:
        return fk.jsonify({'error':'No available Books'}),404
    cur.execute("SELECT MAX(ISSUE_ID) FROM BOOK_ISSUES")
    id=cur.fetchone()[0]
    id=id+1 if id else 0
    if not request['DUE_DATE']:
        cur.execute("SELECT DISSUE FROM LDEFAULT")
        due=cur.fetchone()[0]
        request['DUE_DATE']=due
    cur.execute("INSERT INTO BOOK_ISSUES (ISSUE_ID,BOOK_ID, STUDENT_ID, ISSUE_DATE,RETURN_DATE, STATUS) VALUES (%s,%s, %s, CURDATE(),%s, %s)", (id,request['BOOK_ID'], request['STUDENT_ID'],request['DUE_DATE'], 'Issued'))
    
    if cur.rowcount == 1:
        con.commit()
        cur2.execute("UPDATE BOOK_REQUESTS SET STATUS='Approved' WHERE REQUEST_ID=%s", (request_id,))
        cur.execute("UPDATE BOOKS SET AVAILABLE = AVAILABLE - 1, STATUS='ISSUED' WHERE BOOK_ID = %s",(request['BOOK_ID'],))
        cur.execute("UPDATE STUDENT SET BOOKS_ISSUED = BOOKS_ISSUED + 1,TOTAL_BOOKISSUED=TOTAL_BOOKISSUED+1 WHERE STUDENT_ID = %s", (request['STUDENT_ID'],))
        cur.execute("DELETE FROM BOOK_REQUESTS WHERE REQUEST_ID = %s", (request_id,))
        #cur.execute("INSERT INTO BOOKHISTORY (ISSUE_ID, BOOK_ID, BOOK, STUDENT_ID, STUDENT, ISSUE_DATE, DUE_DATE, RETURN_DATE, DAYS_OVERDUE, FINE, STATUS) VALUES (%s,%s,%s,%s,%s,CURDATE(),DATE_ADD(CURDATE(),INTERVAL %s DAY),NULL,NULL,NULL,'ISSUED')", (request_id, request['BOOK_ID'], request['TITLE'], request['STUDENT_ID'], request['STUDENT_NAME']))
        con.commit()
        
        return fk.jsonify({'status': 'success'})
    else:
        return fk.jsonify({'error': 'Failed to approve request'}), 500
    
@libfile.route('/reject_request', methods=['POST'])
def reject_request():
    data = fk.request.get_json()
    request_id = data.get('requestId')
    reason=data.get('reason')
    
    cur2.execute("SELECT * FROM BOOK_REQUESTS WHERE REQUEST_ID=%s", (request_id,))
    request = cur2.fetchone()
    
    if not request:
        return fk.jsonify({'error': 'Request not found'}), 404
    
    
    cur2.execute("SELECT * FROM BOOK_REQUESTS WHERE REQUEST_ID=%s", (request_id,))
    det=cur2.fetchone()
    cur2.execute("DELETE FROM  BOOK_REQUESTS WHERE REQUEST_ID=%s", (request_id,))
    
    if cur2.rowcount == 1:
        con.commit()
        cur.execute("UPDATE BOOKS SET STATUS='AVAILABLE' WHERE BOOK_ID=%s",(det['BOOK_ID'],))
        #cur.execute("UPDATE BOOKS SET AVAILABLE = AVAILABLE + 1 WHERE BOOK_ID = %s", (det['BOOK_ID'],))
        #cur.execute("INSERT INTO NOTIFICATIONS (STUDENT_ID, TITLE, MESSAGE, DATE, TIME) VALUES (%s, %s, %s, CURDATE(), CURTIME())", 
                    #(det['STUDENT_ID'], 'Book Request Rejected', f'Your request for the book "{det["TITLE"]}" has been rejected.'))
        
        cur.execute("INSERT INTO BOOKHISTORY (ISSUE_ID, BOOK_ID, BOOK, STUDENT_ID, STUDENT, ISSUE_DATE, DUE_DATE, RETURN_DATE, DAYS_OVERDUE, FINE, STATUS,REASON) VALUES (%s,%s,%s,%s,%s,CURDATE(),NULL,NULL,NULL,NULL,'Rejected',%s)", (request_id, det['BOOK_ID'], det['TITLE'], det['STUDENT_ID'], det['STUDENT_NAME'],reason))
        con.commit()
        return fk.jsonify({'status': 'success'})
    else:
        return fk.jsonify({'error': 'Failed to reject request'}), 500
    
@libfile.route('/fine_settings')
def libset():
    if 'lid' and 'lname' not in fk.session:
        return fk.redirect('/librarianlogin')
    cur2.execute("SELECT * FROM LDEFAULT")
    default=cur2.fetchone()
    if default is None:
     default = {'FINE': '', 'DNOTICE': '', 'DISSUE': ''}  # Provide fallback values

    return fk.render_template('fine_settings.html', 
                          df=default['FINE'], 
                          dnotice=default['DNOTICE'], 
                          gp=default['DISSUE'])

  

@libfile.route('/subscription_settings')
def libsubset():
    if 'lid' and 'lname' not in fk.session:
       return fk.redirect('/librarianlogin')
    return fk.render_template('subscription_settings.html')

@libfile.route('/studfine')
def studfine():
    return fk.render_template('studfine.html')

@libfile.route('/savedefault',methods=['POST'])
def save():
    det=fk.request.get_json()
    fine=det.get('fine')
    issuedt=det.get('grace')
    dnot=det.get('dnotice')
    cur.execute("UPDATE LDEFAULT SET FINE=%s,DNOTICE=%s,DISSUE=%s WHERE DID=1",(fine,dnot,issuedt))
    if cur.rowcount==1:
        con.commit()
        return fk.jsonify("Updated")
    else:
        return fk.jsonify("Failed")

@libfile.route('/default',methods=['GET'])
def getd():
    cur2.execute("SELECT * FROM LDEFAULT")
    ldefault=cur2.fetchone()
    if ldefault:
        print(ldefault)
        return fk.jsonify(ldefault)
    else:
        return fk.jsonify("Failed")
    
@libfile.route('/libsendnotice', methods=['POST'])
def lib_send_notice():
    data = fk.request.get_json()
    sid=data.get('student_id')
    date = data.get('date')
    time = dt.datetime.now().time().strftime('%H:%M:%S')  # Auto set current time
    sender = "Librarian"  
    recipient = data.get('recipient')
    subject = data.get('title')
    content = data.get('content')

    if recipient=='Admin':
            cur.execute("""
            INSERT INTO ADMIN_NOTICE (NDATE, NTIME, NFROM, NTO, SUBJECT, CONTENT)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (date, time, sender, recipient, subject, content))
    elif recipient=='All Students' or recipient=='Specific Student':
            if recipient=='All Students':
                sid='All Students'
            cur.execute("INSERT INTO NOTIFICATIONS(STUDENT_ID,TITLE,MESSAGE,DATE,TIME) VALUES(%s,%s,%s,CURDATE(),CURTIME())",(sid,subject,content))
    if cur.rowcount==1:
            con.commit()
            return fk.jsonify({'message': 'Notice sent successfully!'})
    else:
            return fk.jsonify("Failed")
    
@libfile.route('/check_overdue_books', methods=['GET'])
def check_overdue_books():
    try:
        # Get current date
        cur.execute("SELECT CURDATE()")
        today = cur.fetchone()[0]
        
        # Find overdue books that don't have fines yet
        query = """
            SELECT BI.ISSUE_ID, BI.BOOK_ID, BI.STUDENT_ID, S.NAME
            FROM BOOK_ISSUES BI
            JOIN STUDENT S ON BI.STUDENT_ID = S.STUDENT_ID
            LEFT JOIN FINE F ON BI.ISSUE_ID = F.ISSUE_ID
            WHERE 
                BI.RETURN_DATE < %s AND 
                BI.STATUS = 'Issued' AND
                F.FINE_ID IS NULL
        """
        cur2.execute(query, (today,))
        overdue_books = cur2.fetchall()
        
        # Get default fine amount
        cur.execute("SELECT FINE FROM LDEFAULT LIMIT 1")
        fine_amount = cur.fetchone()[0]
        
        # Create fine records for each overdue book
        for book in overdue_books:
            days_overdue = (today - book['RETURN_DATE']).days
            fine = days_overdue * fine_amount
            
            # Update book status to Overdue
            cur.execute("UPDATE BOOK_ISSUES SET STATUS='Overdue' WHERE ISSUE_ID=%s", (book['ISSUE_ID'],))
            
            # Create fine record
            cur.execute("""
                INSERT INTO FINE (
                    STUDENT_ID, SNAME, BOOK_ID, ISSUE_ID, 
                    DUE_DATE, RETURN_DATE, REASON, FINE_AMOUNT
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                book['STUDENT_ID'], book['NAME'], book['BOOK_ID'], book['ISSUE_ID'],
                book['RETURN_DATE'], today, 'Book returned late', fine
            ))
        
        con.commit()
        return fk.jsonify({'message': f'Processed {len(overdue_books)} overdue books'}), 200
        
    except Exception as e:
        con.rollback()
        print(f"Error processing overdue books: {str(e)}")
    return fk.jsonify({'error': str(e)}), 500   
@libfile.route('/api/notices/received', methods=['GET'])
def get_received_admin_notices():
    try:
        cur2.execute("""
            SELECT id, title, content, date, sender, recipient
            FROM notices
            WHERE sender = 'Library Admin' AND recipient IN ('Librarians Only', 'All Staff')
            ORDER BY date DESC
        """)
        data = cur2.fetchall()

        for item in data:
            if isinstance(item.get('date'), dt.date):
                item['date'] = item['date'].isoformat()

        return fk.jsonify({'status': 'success', 'notices': data})
    except Exception as e:
        print(e)
        return fk.jsonify({'status': 'error', 'message': str(e)}), 500

"""@libfile.route('/libsentnotices', methods=['GET'])
def admin_send_notice():
    try:
        all_sent = []

        # ✅ Fetch from ADMIN_NOTICE (sent to other librarians)
        cur2.execute("SELECT * FROM ADMIN_NOTICE WHERE NFROM='Librarian'")
        sent_admin = cur2.fetchall()
        for sent in sent_admin:
            all_sent.append({
                "id": sent['NOTICE_ID'],
                "title": sent['SUBJECT'],
                "content": sent['CONTENT'],
                "date": sent['NDATE'].isoformat() if isinstance(sent['NDATE'], dt.date) else sent['NDATE'],
                "time": str(sent['NTIME']),
                "sender": sent['NFROM'],
                "recipient": sent['NTO'],
                "type": "To Librarian"
            })

        # ✅ Fetch from NOTIFICATIONS (sent to students or admin)
        cur2.execute("SELECT * FROM NOTIFICATIONS WHERE STUDENT_ID IS NOT NULL AND STUDENT_ID != ''")
        sent_students = cur2.fetchall()
        for sent in sent_students:
            all_sent.append({
                "id": sent['NOTIFICATION_ID'],
                "title": sent['TITLE'],
                "content": sent['MESSAGE'],
                "date": sent['DATE'].isoformat() if isinstance(sent['DATE'], dt.date) else sent['DATE'],
                "time": str(sent['TIME']),
                "sender": "Librarian",
                "recipient": sent['STUDENT_ID'],
                "type": "To Student/Admin"
            })

        return fk.jsonify(all_sent)
    except Exception as e:
        print("Error in /libsentnotices:", e)
        return fk.jsonify({'error': str(e)}), 500"""


    



    

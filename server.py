import flask as fk
import mysql.connector as mc
import datetime as dt
import library as lb
from  database import con, cur, cur2
from flask import make_response
import io
from fpdf import FPDF


app = fk.Flask(__name__)
app.register_blueprint(lb.libfile)
app.secret_key='your_secret_key'

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def home():
    fk.session.clear()
    return fk.render_template('index.html')


@app.route('/login')
def log():
    return fk.render_template('login.html')

@app.route('/studentlogin')
def studlog():
    return fk.render_template('studentlogin.html')  

@app.route('/librarianlogin')
def liblog():
    return fk.render_template('librarianlogin.html')

@app.route('/Admindashboard')
def Adm():
    if 'full name' and 'id' not in fk.session:
        return fk.redirect('/login')
    cur.execute("SELECT SUM(OUT_OF) FROM BOOKS")
    tbook=cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM BOOKS")
    titl=cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM BOOK_ISSUES WHERE ACTUAL_RETURN_DATE=CURDATE()")
    avail=cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(AVAILABLE) FROM BOOKS ")
    tavail=cur.fetchone()[0] or 0
    issued=tbook-tavail
    cur.execute("SELECT COUNT(*) FROM STUDENT")
    tstud=cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM ADMIN_NOTICE WHERE RECEIVER='Library Admin' AND READ_STATUS=0")
    unread=cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(FINE_AMOUNT) FROM FINE")
    fines=cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM BOOK_REQUESTS WHERE STATUS='PENDING'")
    pending=cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(FINE_AMOUNT) FROM FINE WHERE PAID=FALSE")
    pfines= cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM LIBRARIAN")
    tlibs=cur.fetchone()[0] or 0
    return fk.render_template('Admindashboard.html',tbooks=tbook, abooks=tavail, ibooks=issued, regstud=tstud, tlib=tlibs, unread=unread, preq=pending, tfines=fines,pfines=pfines)

@app.route('/profile')
def prof():
    if 'full name' and 'id' not in fk.session:
        return fk.redirect('/login')
    return fk.render_template('profile.html',name=fk.session.get('full name'),gender=fk.session.get('gender'),mobile=fk.session.get('mob'),qualify=fk.session.get('qualification'),address=fk.session.get('Address'))

@app.route('/students')
def stud():
    if 'sname' and 'sid' not in fk.session:
        return fk.redirect('/studentlogin')
    return fk.render_template('students.html',name=fk.session.get('sname'),id=fk.session.get('sid'),course=fk.session.get('scourse'),sem=fk.session.get('ssem'),email=fk.session.get('semail'),mobile=fk.session.get('sphone'),bookissued=fk.session.get('sbookissued'),gender=fk.session.get('sgender'))

@app.route('/manage')
def man():
    if 'full name' and 'id' not in fk.session:
        return fk.redirect('/login')
    return fk.render_template('manage.html')

@app.route('/notice')
def notice():
    if 'full name' and 'id' not in fk.session:
        return fk.redirect('/login')
    return fk.render_template('notice.html')

@app.route('/inventory')
def invent():
    if 'full name' and 'id' not in fk.session:
        return fk.redirect('/login')
    return fk.render_template('inventory.html')

@app.route('/studsubscription')
def studscrip():
    return fk.render_template('studsubscription.html')

@app.route('/libhome')
def libhome():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    cur.execute("SELECT SUM(OUT_OF) FROM BOOKS")
    tbook=cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM BOOKS")
    titl=cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM BOOK_ISSUES WHERE ACTUAL_RETURN_DATE=CURDATE()")
    avail=cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(AVAILABLE) FROM BOOKS ")
    tavail=cur.fetchone()[0] or 0
    issued=tbook-tavail
    cur.execute("SELECT COUNT(*) FROM STUDENT")
    tstud=cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM ADMIN_NOTICE WHERE RECEIVER='Library Admin' AND READ_STATUS=0")
    unread=cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(FINE_AMOUNT) FROM FINE")
    fines=cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM BOOK_REQUESTS WHERE STATUS='PENDING'")
    pending=cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(FINE_AMOUNT) FROM FINE WHERE PAID=FALSE")
    pfines= cur.fetchone()[0] or 0
    return fk.render_template('libhome.html',tbooks=tbook, abooks=tavail, ibooks=issued, tstud=tstud, unread=unread, fines=fines, pending=pending, pfines=pfines,titles=titl,avail=avail)

@app.route('/libprofile')
def llog():
     if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
     
     return fk.render_template('libprofile.html',id=fk.session.get('lid'),name=fk.session.get('lname'),email=fk.session.get('lemail'),mobile=fk.session.get('lphone'),gender=fk.session.get('lgender'),qualify=fk.session.get('lqualify'))

@app.route('/libfine')
def libfine():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libfine.html')

@app.route('/libadd_book')
def libaddbook():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libadd_book.html')

@app.route('/libaddstudent')
def libaddstudent():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libaddstudent.html')

@app.route('/libanalytics')
def libanalytic():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libanalytics.html')

@app.route('/libbooks')
def libbook():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libbooks.html')

@app.route('/libhistory')
def libhistory():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libhistory.html')

@app.route('/libmark_attendence')
def libattend():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libmark_attendence.html')

@app.route('/libreturnbook')
def libreturn():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libreturnbook.html')

@app.route('/libsend_notice')
def libsendn():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libsend_notice.html')

@app.route('/libstudents')
def libstud():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libstudents.html')

@app.route('/libview_attendance')
def libview():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libview_attendance.html')

@app.route('/libview_notice')
def libviewn():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libview_notice.html')

@app.route('/libissue')
def bkh():
    if 'lname' and 'lid' not in fk.session:
        return fk.redirect('/librarianlogin')
    return fk.render_template('libissue.html')

@app.route('/log',methods=['POST'])
def check():
    fk.session.clear()
    det=fk.request.get_json()
    user=det.get('username')
    passw=det.get('password')
    cur.execute("SELECT * FROM ADMINP WHERE USERNAME=%s AND PASSWORD=%s",(user,passw))
    res=cur.fetchall()
    if res and res[0][1]==user and res[0][2]==passw:
        fk.session['id']=res[0][0]
        fk.session['full name']=res[0][3]
        fk.session['gender']=res[0][4]
        fk.session['mob']=res[0][5]
        fk.session['qualification']=res[0][6]
        fk.session['Address']=res[0][7]
        return fk.jsonify('Valid')
    else:
        return fk.jsonify('Invalid')

@app.route('/slog',methods=['POST'])
def scheck():
    fk.session.clear()
    det=fk.request.get_json()
    user=det.get('username')
    passw=det.get('password')
    cur.execute("SELECT * FROM STUDENT WHERE USERNAME=%s AND PASSWORD=%s",(user,passw))
    res=cur.fetchall()
    if res and res[0][1]==user and res[0][2]==passw:
        fk.session['sname']=res[0][3]
        fk.session['sid']=res[0][0]
        fk.session['scourse']=res[0][4]
        fk.session['ssem']=res[0][5]
        fk.session['semail']=res[0][6]
        fk.session['sphone']=res[0][7]
        fk.session['sbookissued']=res[0][8]
        #fk.session['sgender']=res[0][9]
        return fk.jsonify('Valid')
    else:
        return fk.jsonify('Invalid')

@app.route('/llog',methods=['POST'])
def lcheck():
    fk.session.clear()
    det=fk.request.get_json()
    user=det.get('username')
    passw=det.get('password')
    cur.execute("SELECT * FROM LIBRARIAN WHERE USERNAME=%s AND PASSWORD=%s",(user,passw))
    res=cur.fetchall()
    if res and res[0][1]==user and res[0][2]==passw:
        fk.session['lid']=res[0][0]
        fk.session['lname']=res[0][3]
        fk.session['lemail']=res[0][4]
        fk.session['lgender']=res[0][5]
        fk.session['lphone']=res[0][6]
        fk.session['lqualify']=res[0][7]
        return fk.jsonify('Valid')
    else:
        return fk.jsonify('Invalid')

@app.route('/update',methods=['POST'])
def update():
    udet=fk.request.get_json()
    role=udet.get('Role')
    if role=='ADMINP':
        fname=udet.get('name')
        mob=udet.get('mobile')
        cou=udet.get('course')
        add=udet.get('address')
        cur.execute("UPDATE ADMINP SET FULL_NAME=%s,MOBILE_NUMBER=%s,QUALIFICATION=%s,ADDRESS=%s WHERE ADMIN_ID=%s",(fname,mob,cou,add,int(fk.session.get('id'))))
    elif role=='STUDENT':
        sfname=udet.get('sname')
        scourse=udet.get('scourse')
        ssem=udet.get('ssemester')
        semail=udet.get('semail')
        sphone=udet.get('sphone')
        cur.execute("UPDATE STUDENT SET NAME=%s,COURSE=%s,SEMESTER=%s,EMAIL=%s,MOBILE_NO=%s WHERE STUDENT_ID=%s",(sfname,scourse,ssem,semail,sphone,int(fk.session.get('sid'))))
    elif role=='LIBRARIAN':
        lname=udet.get('name')
        lemail=udet.get('email')
        lphone=udet.get('mobile')
        lqualify=udet.get('qualify')
        fk.session['lname']=lname
        fk.session['lemail']=lemail
        fk.session['lphone']=lphone
        fk.session['lqualify']=lqualify
        cur.execute("UPDATE LIBRARIAN SET NAME=%s,EMAIL=%s,MOBILE_NO=%s,QUALIFICATION=%s WHERE LIBRARIAN_ID=%s",(lname,lemail,lphone,lqualify,int(fk.session.get('lid'))))
    elif role=='LSTUDENT':
        sid=udet.get('id')
        print(sid)
        sfname=udet.get('sname')
        print(sfname   )
        scourse=udet.get('scourse')
        print(scourse)
        ssem=udet.get('ssemester')
        print(ssem)
        semail=udet.get('semail')
        print(semail)
        sphone=udet.get('sphone')
        print(sphone)
        user=udet.get('suser')
        print(user)
        passw=udet.get('spass')
        print(passw)
        cur.execute("UPDATE STUDENT SET NAME=%s,COURSE=%s,SEMESTER=%s,EMAIL=%s,MOBILE_NO=%s,USERNAME=%s,PASSWORD=%s WHERE STUDENT_ID=%s",(sfname,scourse,ssem,semail,sphone,user,passw,sid))
       
    if cur.rowcount==1:
        con.commit()
        return fk.jsonify("Updated"),200
    else:
        return fk.jsonify("Failed"),400

@app.route('/lib')
def lib():
    cur2.execute("SELECT * FROM LIBRARIAN")
    rows=cur2.fetchall()
    return fk.jsonify({"librarian":rows})

@app.route('/addlib',methods=['POST'])
def addlib():
    adet=fk.request.get_json()
    nam=adet.get('name')
    email=adet.get('email')
    gender=adet.get('gender')
    mobile=adet.get('mobile')
    qualification=adet.get('qual')
    user=adet.get('username')
    passw=adet.get('password')
    cur.execute("INSERT INTO LIBRARIAN(USERNAME,PASSWORD,NAME,EMAIL,GENDER,MOBILE_NO,QUALIFICATION) VALUES(%s,%s,%s,%s,%s,%s,%s)",(user,passw,nam,email,gender,mobile,qualification))
    if cur.rowcount==1:
        con.commit()
        return fk.jsonify("Updated")
    else:
        return fk.jsonify("Failed")

@app.route('/remlib',methods=['POST'])
def remove():
    rdet=fk.request.get_json()
    id=rdet.get('lid')
    cur.execute("DELETE FROM LIBRARIAN WHERE LIBRARIAN_ID=%s",[id])
    print(cur.rowcount)
    print(id)
    if cur.rowcount==1:
        con.commit()
        return fk.jsonify("Deleted")
    else:
        return fk.jsonify("Failed")

@app.route('/book',methods=['GET'])
def book():
    cur2.execute("SELECT * FROM BOOKS")
    rows=cur2.fetchall()

    
    return fk.jsonify({"book":rows})

@app.route('/loadNotices')
def ln():
    cur2.execute("SELECT * FROM ADMIN_NOTICE")
    data=cur2.fetchall()
    for item in data:
       if isinstance(item.get('NDATE'), dt.date):
            item['NDATE'] = item['NDATE'].isoformat()
       if isinstance(item.get('NTIME'), dt.timedelta):
            total_seconds = int(item['NTIME'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            item['NTIME'] = f"{hours:02}:{minutes:02}:{seconds:02}"
    return fk.jsonify(data)

@app.route('/addnot',methods=['POST'])
def addN():
    ndet=fk.request.get_json()
    send=ndet.get('sender')
    to=ndet.get('receiver')
    subject=ndet.get('subject')
    message=ndet.get('message')
    print(to)
    if to =='All Students':
        cur.execute("INSERT INTO NOTIFICATIONS(STUDENT_ID,TITLE,MESSAGE,DATE,TIME) VALUES(%s,%s,%s,CURDATE(),CURTIME())",(to,subject,message))
    elif to == 'Librarians Only':
        cur.execute("INSERT INTO ADMIN_NOTICE(NDATE,NTIME,NFROM,NTO,SUBJECT,CONTENT) VALUES(CURDATE(),CURTIME(),%s,%s,%s,%s)",(send,to,subject,message))
    if cur.rowcount==1:
        con.commit()
        return fk.jsonify("Sent")
    else:
        return fk.jsonify("Failed")
    
@app.route('/delnot',methods=['POST'])
def deln():
        det=fk.request.get_json()
        did=det.get('nid')
        cur.execute("DELETE FROM ADMIN_NOTICE WHERE NOTICE_ID=%s",(did,))
        if cur.rowcount==1:
            con.commit()
            return fk.jsonify("Deleted")
        else:
            return fk.jsonify("Failed")
        
@app.route('/studentdashboard')
def student_dashboard():
    if 'sid' not in fk.session:
        return fk.redirect('/studentlogin')
    
    student_id = fk.session['sid']
    
    cur2.execute("SELECT * FROM STUDENT WHERE STUDENT_ID=%s", (student_id,))
    student = cur2.fetchone()
    cur.execute("SELECT COUNT(*) FROM BOOK_ISSUES WHERE STUDENT_ID=%s AND STATUS='Issued'", (student_id,))
    issued_books = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM NOTIFICATIONS WHERE STUDENT_ID=%s AND READ_STATUS=0", (student_id,))
    unread_notifications = cur.fetchone()[0]
    
    return fk.jsonify({"student":student,"issued_books":issued_books,"unread_notifications":unread_notifications})

@app.route('/student_books')
def student_books():
    if 'sid' not in fk.session:
        return fk.jsonify({'error': 'Unauthorized'}), 401
    
    student_id = fk.session['sid']
    cur2.execute("SELECT * FROM BOOK_REQUESTS WHERE STUDENT_ID = %s", (student_id,))
    books = cur2.fetchall()
    
    for book in books:
        if 'REQUEST_DATE' in book and isinstance(book['REQUEST_DATE'], dt.date):
            book['REQUEST_DATE'] = book['REQUEST_DATE'].isoformat()
    return fk.jsonify({'books': books})

@app.route('/student_notifications')
def student_notifications():
    if 'sid' not in fk.session:
        return fk.jsonify({'error': 'Unauthorized'}), 401
    
    student_id = fk.session['sid']
    cur2.execute("""
        SELECT NOTIFICATION_ID, TITLE, MESSAGE, DATE, TIME, READ_STATUS 
        FROM NOTIFICATIONS 
        WHERE STUDENT_ID = %s OR STUDENT_ID='All Students' 
        ORDER BY DATE DESC, TIME DESC
    """, (student_id,))
    notifications = cur2.fetchall()
    
    for notification in notifications:
        if 'DATE' in notification and isinstance(notification['DATE'], dt.date):
            notification['DATE'] = notification['DATE'].isoformat()
        if 'TIME' in notification and isinstance(notification['TIME'], dt.timedelta):
            total_seconds = int(notification['TIME'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            notification['TIME'] = f"{hours:02}:{minutes:02}:{seconds:02}"
    
    return fk.jsonify({'notifications': notifications})

@app.route('/mark_notification_read', methods=['POST'])
def mark_notification_read():
    if 'sid' not in fk.session:
        return fk.jsonify({'error': 'Unauthorized'}), 401
    
    data = fk.request.get_json()
    notification_id = data.get('notification_id')
    
    cur.execute("""
        UPDATE NOTIFICATIONS 
        SET READ_STATUS = 1 
        WHERE NOTIFICATION_ID = %s AND STUDENT_ID = %s
    """, (notification_id, fk.session['sid']))
    
    if cur.rowcount == 1:
        con.commit()
        return fk.jsonify({'status': 'success'})
    else:
        return fk.jsonify({'error': 'Notification not found'}), 404

@app.route('/request_book', methods=['POST'])
def request_book():
    if 'sid' not in fk.session:
        return fk.jsonify({'error': 'Unauthorized'}), 401
    
    data = fk.request.get_json()
    book_id = data.get('book_id')
    
    
    cur.execute("SELECT STATUS,TITLE,PUBLISHER FROM BOOKS WHERE BOOK_ID = %s", (book_id,))
    result = cur.fetchall()
    
    if not result:
        return fk.jsonify({'error': 'Book not found'}), 404
    
    if result[0][0] != 'AVAILABLE':
        return fk.jsonify({'error': 'Book is not available'}), 400
    
    cur.execute("SELECT * FROM BOOK_REQUESTS WHERE BOOK_ID = %s OR STUDENT_ID = %s AND STATUS = 'PENDING'", (book_id, fk.session['sid']))
    breq=cur.fetchall()
    if not breq :
        cur.execute("""
        INSERT INTO BOOK_REQUESTS 
        (BOOK_ID, STUDENT_ID, REQUEST_DATE, STATUS,TITLE,PUBLISHER,STUDENT_NAME) 
        VALUES (%s, %s, CURDATE(), 'PENDING',%s,%s,%s)
        """, (book_id, fk.session['sid'], result[0][1], result[0][2], fk.session.get('sname')))

        if cur.rowcount == 1:
            cur.execute("UPDATE BOOKS SET STATUS = 'REQUESTED' WHERE BOOK_ID = %s", (book_id,))
            con.commit()
            return fk.jsonify({'status': 'success'})
        else:
            return fk.jsonify({'error': 'Failed to create request'}), 500
    else:
        return fk.jsonify({'error': 'You have already requested this book or it is already requested by another student'}), 400

@app.route('/studentnotice', methods=['POST'])
def send_notice():
    data = fk.request.get_json()

    title = data.get('title')
    content = data.get('content')
    date = data.get('date', dt.datetime.today().strftime('%Y-%m-%d'))
    sender = data.get('sender')
    recipient = data.get('recipient')
    student_id = data.get('student_id', '')
    student_name = data.get('student_name', '')
    course = data.get('course', '')

    try:

        cur.execute("""
            INSERT INTO NOTIFICATIONS (STUDENT_ID,TITLE, MESSAGE, DATE, TIME)
            VALUES (%s, %s, %s,CURDATE(), CURTIME())
        """, (student_id,title, content))
        con.commit()
        return fk.jsonify({"message": "Notice sent successfully!"})
    except Exception as e:
        return fk.sonify({"message": f"Error sending notice: {str(e)}"}), 500

# ✅ Route to render frontend form
@app.route('/libsend_notice')
def send_notice_form():
    return fk.render_template("libsend_notice.html")

# ✅ API: Fetch notices
@app.route('/api/notices/new', methods=['GET'])
def get_new_notices():
    username = 'Library Admin'

    
    print(username)
    
    cur2.execute("""
            SELECT *
            FROM ADMIN_NOTICE
            WHERE NFROM = 'Admin'  AND NTO='Librarians Only'
            ORDER BY NDATE DESC;
    """)
    rows = cur2.fetchall()
    print(rows)
    for row in rows:
            if isinstance(row['NDATE'], dt.datetime):
                row['NDATE'] = row['NDATE'].isoformat()
            if isinstance(row['NTIME'], dt.timedelta):
                total_seconds = int(row['NTIME'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                row['NTIME'] = f"{hours:02}:{minutes:02}:{seconds:02}"

    return fk.jsonify({'status': 'success', 'notices': rows})
    

# ✅ API: Delete a notice
@app.route('/api/notices/delete', methods=['POST'])
def delete_notice():
    data = fk.request.get_json()
    notice_id = data.get('id')

    
    try:
        cur.execute("DELETE FROM notices WHERE id = %s", (notice_id,))
        con.commit()
        return fk.jsonify({'status': 'success'})
    except Exception as e:
        return fk.jsonify({'status': 'error', 'message': str(e)})
    


@app.route('/search_student', methods=['POST'])
def search_student():
    data = fk.request.get_json()
    student_id = data.get('student_id')
    
    if not student_id:
        return fk.jsonify({'error': 'Student ID is required'}), 400
    
    try:
        
        
        cur2.execute("SELECT NAME,COURSE FROM STUDENT WHERE STUDENT_ID = %s", (student_id,))
        student = cur2.fetchone()
        
        if student:
            return fk.jsonify({
                'success': True,
                'name': student['NAME'],
                'student_id': student_id,
                'dep': student['COURSE']
            })
        else:
            return fk.jsonify({'error': 'Student not found'}), 404
            
    except Exception as e:
        return fk.jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals(): cur.close()
        if 'conn' in locals(): con.close()

@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    data = fk.request.get_json()
    student_id = data.get('student_id')
    status = data.get('status')
    today = dt.datetime.now().date()
    
    if not student_id or not status:
        return fk.jsonify({'error': 'Student ID and status are required'}), 400
    
    try:
      
        
        # Check if student exists
        cur.execute("SELECT 1 FROM STUDENT WHERE STUDENT_ID = %s", (student_id,))
        if not cur.fetchone():
            return fk.jsonify({'error': 'Student not found'}), 404
        
        # Check if attendance already marked today (optional)
        cur.execute("""
            SELECT 1 FROM MARK_ATTENDANCE 
            WHERE STUDENT_ID = %s AND DATE = %s
        """, (student_id, today))
        if cur.fetchone():
            return fk.jsonify({'error': 'Attendance already marked for today'}), 400
        
        # Insert attendance record
        cur.execute("""
            INSERT INTO MARK_ATTENDANCE (STUDENT_ID, DATE, STATUS)
            VALUES (%s, %s, %s)
        """, (student_id, today, status))
        
        con.commit()
        return fk.jsonify({
            'success': True,
            'message': f'Attendance marked as {status} for student {student_id}'
        })
        
    except Exception as e:
        if 'con' in locals(): con.rollback()
        return fk.jsonify({'error': str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'con' in locals(): con.close()

@app.route('/api/get_attendance')
def get_attendance():
    try:
        from_date = fk.request.args.get('fromDate')
        to_date = fk.request.args.get('toDate')
        student_id = fk.request.args.get('studentId')
        status = fk.request.args.get('status')
        query = """
        SELECT a.ID, a.STUDENT_ID, a.DATE, a.STATUS
        FROM MARK_ATTENDANCE a
        WHERE 1=1
        """
        params = []
        if from_date:
            query += " AND a.DATE >= %s"
            params.append(from_date)
        if to_date:
            query += " AND a.DATE <= %s"
            params.append(to_date)
        if student_id:
            query += " AND a.STUDENT_ID = %s"
            params.append(student_id)
        if status:
            query += " AND a.STATUS = %s"
            params.append(status)
            
        query += " ORDER BY a.DATE DESC"

        cur.execute(query, params)
        attendance_data = cur.fetchall()
        for record in attendance_data:
            if record['DATE']:
                record['DATE'] = record['DATE'].strftime('%Y-%m-%d')
        return fk.jsonify(attendance_data)
        
    except Exception as e:
        print("Error fetching attendance:", str(e))
        return fk.jsonify({'error': str(e)}), 500
    #view attendance 
@app.route('/api/view_attendance', methods=['POST'])
def view_attendance():
    data = fk.request.get_json()
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    search = data.get('search', '').strip().lower()

    query = """
        SELECT M.ID, S.STUDENT_ID, S.NAME, M.DATE, M.STATUS
        FROM MARK_ATTENDANCE M
        JOIN STUDENT S ON M.STUDENT_ID = S.STUDENT_ID
        WHERE 1=1
    """
    params = []

    if from_date:
        query += " AND M.DATE >= %s"
        params.append(from_date)
    if to_date:
        query += " AND M.DATE <= %s"
        params.append(to_date)
    if search:
        query += " AND LOWER(S.NAME) LIKE %s"
        params.append(f"%{search}%")

    try:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row[0],  
                "student_id": row[1],
                "student_name": row[2],
                "date": row[3].strftime("%Y-%m-%d"),
                "status": row[4]
            })

        return fk.jsonify({"status": "success", "data": results})

    except Exception as e:
        return fk.jsonify({"status": "error", "message": str(e)})
    
@app.route('/api/analytics', methods=['GET'])
def analytics_data():
    try:
        # Use a single dictionary cursor for all queries
        cur2.execute("SELECT COUNT(*) AS total FROM BOOKS")
        total_books = cur2.fetchone()['total'] or 0

        cur2.execute("SELECT COALESCE(SUM(AVAILABLE), 0) AS available FROM BOOKS")
        available_books = cur2.fetchone()['available']

        cur2.execute("SELECT COALESCE(SUM(OUT_OF - AVAILABLE), 0) AS issued FROM BOOKS")
        issued_books = cur2.fetchone()['issued']

        cur2.execute("SELECT COUNT(*) AS students FROM STUDENT")
        registered_students = cur2.fetchone()['students'] or 0

        # Most issued books (Featured Books)
        cur2.execute("""
            SELECT 
                B.TITLE, 
                B.AUTHOR, 
                B.AVAILABLE, 
                B.OUT_OF, 
                (B.OUT_OF - B.AVAILABLE) AS ISSUED_COUNT,
                B.PUBLISHER,
                B.BDESCRIPTION AS DESCRIPTION
            FROM BOOKS B
            ORDER BY ISSUED_COUNT DESC
            LIMIT 4
        """)
        featured_books = cur2.fetchall()

        # Ensure all required fields are present in each book
        for book in featured_books:
            book['AVAILABLE'] = book.get('AVAILABLE', 0)
            book['OUT_OF'] = book.get('OUT_OF', 0)
            book['ISSUED_COUNT'] = book.get('ISSUED_COUNT', 0)
            book['DESCRIPTION'] = book.get('DESCRIPTION', 'No description available')

        return fk.jsonify({
            "status": "success",
            "data": {
                "total_books": total_books,
                "available_books": available_books,
                "issued_books": issued_books,
                "registered_students": registered_students,
                "featured_books": featured_books
            }
        })

    except Exception as e:
        
        app.logger.error(f"Error in analytics endpoint: {str(e)}")
        return fk.jsonify({
            "status": "error",
            "message": "Failed to fetch analytics data",
            "error": str(e)
        }), 500

@app.route('/searchbooks')
def search_books():
    title = fk.request.args.get('title', '').strip()
    author = fk.request.args.get('author', '').strip()
    category = fk.request.args.get('category', '').strip()
    
   
    if not (title or author or category):
        return fk.jsonify([])
    
    query = "SELECT BOOK_ID, TITLE, AUTHOR, ISBN, CATEGORY, STATUS FROM BOOKS WHERE 1=1"
    params = []
    
    if title:
        query += " AND LOWER(TITLE) LIKE LOWER(%s)"
        params.append(f"%{title}%")
    if author:
        query += " AND LOWER(AUTHOR) LIKE LOWER(%s)"
        params.append(f"%{author}%")
    if category:
        query += " AND CATEGORY = %s"
        params.append(category)
    
    query += " ORDER BY TITLE"
    
    try:
        cur2.execute(query, params)
        books = cur2.fetchall()
        
        # Convert date objects to strings if needed
        for book in books:
            if 'PUBLISHED_DATE' in book and isinstance(book['PUBLISHED_DATE'], dt.date):
                book['PUBLISHED_DATE'] = book['PUBLISHED_DATE'].isoformat()
        
        return fk.jsonify(books)
    except Exception as e:
        print(f"Database error: {e}")
        return fk.jsonify({'error': 'Database error'}), 500

@app.route('/loadReceivedNotices')
def load_received_notices():
    cur2.execute("""
        SELECT * FROM ADMIN_NOTICE 
        WHERE NFROM = 'Librarian' 
        ORDER BY NDATE DESC, NTIME DESC
    """)
    data = cur2.fetchall()
    for item in data:
        if isinstance(item.get('NDATE'), dt.date):
            item['NDATE'] = item['NDATE'].isoformat()
        if isinstance(item.get('NTIME'), dt.timedelta):
            total_seconds = int(item['NTIME'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            item['NTIME'] = f"{hours:02}:{minutes:02}:{seconds:02}"
    return fk.jsonify(data)

@app.route('/api/books/department')
def get_books_by_department():
    department = fk.request.args.get('department')
    semester = fk.request.args.get('semester', type=int)
    print(department)
    if not department:
        return fk.jsonify({'error': 'Department is required'}), 400
    
    try:
        query = "SELECT BOOK_ID, TITLE, AUTHOR, ISBN, STATUS FROM BOOKS WHERE DEPARTMENT = %s"
        params = [department]
        
        if semester:
            query += " AND SEMESTER = %s"
            params.append(semester)
        
        query += " ORDER BY TITLE"
        
        cur2.execute(query, params)
        books = cur2.fetchall()
        print(books)
        return fk.jsonify(books)
    except Exception as e:
        return fk.jsonify({'error': str(e)}), 500
    
@app.route('/api/trending_books')
def get_trending_books():
    try:
        # Get most borrowed books (you can adjust this query based on your criteria)
        cur2.execute("""
            SELECT b.BOOK_ID, b.TITLE, b.AUTHOR, b.ISBN, b.STATUS, COUNT(bi.ISSUE_ID) as borrow_count
            FROM BOOKS b
            LEFT JOIN BOOK_ISSUES bi ON b.BOOK_ID = bi.BOOK_ID
            GROUP BY b.BOOK_ID, b.TITLE, b.AUTHOR, b.ISBN, b.STATUS
            ORDER BY borrow_count DESC
            LIMIT 10
        """)
        most_borrowed = cur2.fetchall()

        # Get newest books
        cur2.execute("""
            SELECT BOOK_ID, TITLE, AUTHOR, ISBN, STATUS, YEAR
            FROM BOOKS
            ORDER BY YEAR DESC
            LIMIT 10
        """)
        newest = cur2.fetchall()

        return fk.jsonify({
            'most_borrowed': most_borrowed,
            'newest': newest
        })
    except Exception as e:
        return fk.jsonify({'error': str(e)}), 500

"""cur2.execute("SELECT * FROM STUDENT")
students=cur2.fetchall()


def get_end_date(start_date, months):
    end_date = start_date + dt.timedelta(days=30*months)
    return end_date.strftime('%Y-%m-%d')



@app.route('/add_subscription', methods=['GET', 'POST'])
def add_subscription():
    if fk.request.method == 'POST':
        data = fk.request.get_json()
        
        # Find student
        student = next((s for s in students if s['id'] == data['studentId'] or s['name'].lower() == data['studentName'].lower()), None)
        if not student:
            return fk.jsonify({"success": False, "message": "Student not found"}), 404
        
        # Create new subscription
        new_sub = {
            "id": f"SUB{len(subscriptions) + 1000}",
            "studentId": student['id'],
            "studentName": student['name'],
            "plan": data['plan'],
            "startDate": dt.datetime.now().strftime('%Y-%m-%d'),
            "endDate": get_end_date(dt.datetime.now(), 1),
            "amount": plans[data['plan']]['priceValue'],
            "status": "active",
            "paymentMethod": data['paymentMethod'],
            "transactionId": data.get('transactionId')
        }
        
        subscriptions.append(new_sub)
        
        return fk.jsonify({
            "success": True,
            "message": "Subscription added successfully",
            "subscription": new_sub
        })
    
    return fk.render_template('addsubscription.html', plans=plans)

@app.route('/search_student', methods=['POST'])
def search_student():
    search_term = request.json.get('query', '').lower()
    if len(search_term) < 3:
        return jsonify([])
    
    results = [s for s in students 
               if search_term in s['id'].lower() or search_term in s['name'].lower()]
    
    return jsonify(results)

@app.route('/get_subscriptions', methods=['GET'])
def get_subscriptions():
    status_filter = request.args.get('status')
    plan_filter = request.args.get('plan')
    search_filter = request.args.get('search', '').lower()
    
    filtered = subscriptions
    
    if status_filter:
        filtered = [s for s in filtered if s['status'] == status_filter]
    
    if plan_filter:
        filtered = [s for s in filtered if s['plan'] == plan_filter]
    
    if search_filter:
        filtered = [s for s in filtered 
                   if search_filter in s['studentId'].lower() 
                   or search_filter in s['studentName'].lower()]
    
    return fk.jsonify(filtered)

@app.route('/renew_subscription/<sub_id>', methods=['POST'])
def renew_subscription(sub_id):
    sub = next((s for s in subscriptions if s['id'] == sub_id), None)
    if not sub:
        return fk.jsonify({"success": False, "message": "Subscription not found"}), 404
    
    today = dt.datetime.now()
    sub['startDate'] = today.strftime('%Y-%m-%d')
    sub['endDate'] = get_end_date(today, 1)
    sub['status'] = "active"
    
    return fk.jsonify({
        "success": True,
        "message": "Subscription renewed successfully",
        "subscription": sub
    })

@app.route('/download_receipt', methods=['POST'])
def download_receipt():
    data = fk.request.get_json()
    
    # Find student
    student = next((s for s in students if s['id'] == data['studentId'])), None
    if not student:
        return fk.jsonify({"success": False, "message": "Student not found"}), 404
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(40, 53, 147)
    pdf.cell(0, 10, 'GP LIBRARY', 0, 1, 'C')
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Subscription Receipt', 0, 1, 'C')
    
    # Receipt details
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Receipt No: SUB-{len(subscriptions) + 1000}", 0, 1)
    pdf.cell(0, 10, f"Date: {dt.datetime.now().strftime('%Y-%m-%d')}", 0, 1)
    
    # Student info
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(40, 53, 147)
    pdf.cell(0, 10, 'Student Information', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Name: {student['name']}", 0, 1)
    pdf.cell(0, 10, f"ID: {student['id']}", 0, 1)
    pdf.cell(0, 10, f"Department: {student['department']}", 0, 1)
    
    # Subscription details
    plan = plans[data['plan']]
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(40, 53, 147)
    pdf.cell(0, 10, 'Subscription Details', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Plan: {plan['name']}", 0, 1)
    pdf.cell(0, 10, f"Duration: {plan['duration']}", 0, 1)
    pdf.cell(0, 10, f"Amount: {plan['price']}", 0, 1)
    payment_method = 'Cash' if data['paymentMethod'] == 'cash' else f"Transaction (ID: {data['transactionId']})"
    pdf.cell(0, 10, f"Payment Method: {payment_method}", 0, 1)
    
    # Footer
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Thank you for your subscription!', 0, 1, 'C')
    
    # Save to buffer
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    
    return fk.send_file(
        buffer,
        as_attachment=True,
        download_name=f"subscription_receipt_{student['name'].replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/generate_report', methods=['GET'])
def generate_report():
    status_filter = fk.request.args.get('status')
    plan_filter = fk.request.args.get('plan')
    search_filter = fk.request.args.get('search', '').lower()
    
    filtered = subscriptions
    
    if status_filter:
        filtered = [s for s in filtered if s['status'] == status_filter]
    
    if plan_filter:
        filtered = [s for s in filtered if s['plan'] == plan_filter]
    
    if search_filter:
        filtered = [s for s in filtered 
                   if search_filter in s['studentId'].lower() 
                   or search_filter in s['studentName'].lower()]
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(40, 53, 147)
    pdf.cell(0, 10, 'GP LIBRARY', 0, 1, 'C')
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Monthly Subscription Report', 0, 1, 'C')
    
    # Report details
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Generated on: {dt.datetime.now().strftime('%Y-%m-%d')}", 0, 1)
    pdf.cell(0, 10, f"Total Subscriptions: {len(filtered)}", 0, 1)
    
    # Summary statistics
    active_count = len([s for s in filtered if s['status'] == 'active'])
    expired_count = len([s for s in filtered if s['status'] == 'expired'])
    pending_count = len([s for s in filtered if s['status'] == 'pending'])
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(40, 53, 147)
    pdf.cell(0, 10, 'Status Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Active: {active_count}", 0, 1)
    pdf.cell(0, 10, f"Expired: {expired_count}", 0, 1)
    pdf.cell(0, 10, f"Pending: {pending_count}", 0, 1)
    
    # Plan statistics
    basic_count = len([s for s in filtered if s['plan'] == 'basic'])
    standard_count = len([s for s in filtered if s['plan'] == 'standard'])
    premium_count = len([s for s in filtered if s['plan'] == 'premium'])
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(40, 53, 147)
    pdf.cell(0, 10, 'Plan Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Basic: {basic_count}", 0, 1)
    pdf.cell(0, 10, f"Standard: {standard_count}", 0, 1)
    pdf.cell(0, 10, f"Premium: {premium_count}", 0, 1)
    
    # Financial summary
    total_revenue = sum(s['amount'] for s in filtered)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(40, 53, 147)
    pdf.cell(0, 10, 'Financial Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Total Revenue: ₹{total_revenue}", 0, 1)
    
    # Detailed records
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(40, 53, 147)
    pdf.cell(0, 10, 'Detailed Records', 0, 1)
    
    # Table header
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(40, 53, 147)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 10, 'ID', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'Student ID', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'Name', 1, 0, 'C', 1)
    pdf.cell(30, 10, 'Plan', 1, 0, 'C', 1)
    pdf.cell(20, 10, 'Amount', 1, 0, 'C', 1)
    pdf.cell(20, 10, 'Status', 1, 0, 'C', 1)
    pdf.cell(25, 10, 'Start Date', 1, 0, 'C', 1)
    pdf.cell(25, 10, 'End Date', 1, 1, 'C', 1)
    
    # Table rows
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    for sub in filtered:
        pdf.cell(30, 10, sub['id'], 1)
        pdf.cell(30, 10, sub['studentId'], 1)
        pdf.cell(40, 10, sub['studentName'], 1)
        pdf.cell(30, 10, plans[sub['plan']]['name'], 1)
        pdf.cell(20, 10, f"₹{sub['amount']}", 1)
        pdf.cell(20, 10, sub['status'].capitalize(), 1)
        pdf.cell(25, 10, sub['startDate'], 1)
        pdf.cell(25, 10, sub['endDate'], 1)
        pdf.ln()
    
    # Save to buffer
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    
    return fk.send_file(
        buffer,
        as_attachment=True,
        download_name=f"subscription_report_{dt.datetime.now().strftime('%Y-%m-%d')}.pdf",
        mimetype='application/pdf'
    )"""

@app.route('/fines', methods=['GET'])
def get_fines():
    try:
        # Get filter parameters from request
        status_filter = fk.request.args.get('status', 'all')
        search_term = fk.request.args.get('search', '').lower()
        start_date = fk.request.args.get('startDate')
        end_date = fk.request.args.get('endDate')

        # Base query
        query = """
            SELECT 
                F.FINE_ID, F.STUDENT_ID, F.SNAME, 
                F.BOOK_ID, B.TITLE AS BOOK_TITLE, F.ISSUE_ID,
                F.DUE_DATE, F.RETURN_DATE, F.REASON, 
                F.FINE_AMOUNT, F.PAID, F.TRANSACTION_ID
            FROM FINE F
            LEFT JOIN BOOKS B ON F.BOOK_ID = B.BOOK_ID
            WHERE 1=1
        """
        params = []

        # Apply status filter
        if status_filter != 'all':
            query += " AND F.PAID = %s"
            params.append(1 if status_filter == 'paid' else 0)

        # Apply date range filter
        if start_date:
            query += " AND F.RETURN_DATE >= %s"
            params.append(start_date)
        if end_date:
            query += " AND F.RETURN_DATE <= %s"
            params.append(end_date)

        # Apply search filter
        if search_term:
            query += " AND (LOWER(F.SNAME) LIKE %s OR CAST(F.STUDENT_ID AS CHAR) LIKE %s OR LOWER(B.TITLE) LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])

        query += " ORDER BY F.RETURN_DATE DESC"

        cur2.execute(query, params)
        fines = cur2.fetchall()

        # Convert data types for frontend
        for fine in fines:
            fine['DUE_DATE'] = fine['DUE_DATE'].isoformat() if fine['DUE_DATE'] else None
            fine['RETURN_DATE'] = fine['RETURN_DATE'].isoformat() if fine['RETURN_DATE'] else None
            fine['PAID'] = bool(fine['PAID'])
            fine['FINE_AMOUNT'] = float(fine['FINE_AMOUNT']) if fine['FINE_AMOUNT'] is not None else 0.0

        return fk.jsonify(fines)

    except Exception as e:
        return fk.jsonify({'error': str(e)}), 500

@app.route('/fine_stats', methods=['GET'])
def get_fine_stats():
    try:
        today = dt.date.today().isoformat()
        
        # Today's collection
        cur.execute("""
            SELECT COALESCE(SUM(FINE_AMOUNT), 0) AS today_total 
            FROM FINE 
            WHERE PAID = TRUE AND RETURN_DATE = %s
        """, (today,))
        today_total = float(cur.fetchone()[0])

        # Pending fines
        cur.execute("""
            SELECT COALESCE(SUM(FINE_AMOUNT), 0) AS pending_total 
            FROM FINE 
            WHERE PAID = FALSE
        """)
        pending_total = float(cur.fetchone()[0])

        # Total collection
        cur.execute("""
            SELECT COALESCE(SUM(FINE_AMOUNT), 0) AS total_amount 
            FROM FINE 
            WHERE PAID = TRUE
        """)
        total_amount = float(cur.fetchone()[0])

        return fk.jsonify({
            'today_total': today_total,
            'pending_total': pending_total,
            'total_amount': total_amount
        })

    except Exception as e:
        return fk.jsonify({'error': str(e)}), 500

@app.route('/mark_paid/<int:fine_id>', methods=['POST'])
def mark_fine_paid(fine_id):
    try:
        # Generate transaction ID
        transaction_id = f"TXN{dt.datetime.now().strftime('%Y%m%d%H%M%S')}{fine_id:04d}"
        
        cur.execute("""
            UPDATE FINE 
            SET PAID = TRUE, TRANSACTION_ID = %s 
            WHERE FINE_ID = %s
        """, (transaction_id, fine_id))
        
        if cur.rowcount == 1:
            con.commit()
            return fk.jsonify({
                'status': 'success', 
                'transaction_id': transaction_id,
                'paid': True
            })
        else:
            return fk.jsonify({'error': 'Fine not found'}), 404

    except Exception as e:
        con.rollback()
        return fk.jsonify({'error': str(e)}), 500
@app.route('/student_fines/<int:student_id>', methods=['GET'])
def get_student_fines(student_id):
    try:
        # Get current date
        cur.execute("SELECT CURDATE()")
        today = cur.fetchone()[0]
        
        # Query to get overdue books with fine details
        query = """
            SELECT 
                BI.ISSUE_ID,
                BI.BOOK_ID,
                B.TITLE,
                B.AUTHOR,
                BI.ISSUE_DATE,
                BI.RETURN_DATE,
                DATEDIFF(%s, BI.RETURN_DATE) AS DAYS_OVERDUE,
                (DATEDIFF(%s, BI.RETURN_DATE) * (SELECT FINE FROM LDEFAULT LIMIT 1)) AS FINE_AMOUNT,
                F.FINE_ID,
                F.PAID,
                F.TRANSACTION_ID,
                F.PAYMENT_DATE
            FROM BOOK_ISSUES BI
            JOIN BOOKS B ON BI.BOOK_ID = B.BOOK_ID
            LEFT JOIN FINE F ON BI.ISSUE_ID = F.ISSUE_ID
            WHERE 
                BI.STUDENT_ID = %s AND 
                (BI.STATUS = 'Overdue' OR (F.FINE_ID IS NOT NULL AND F.PAID = FALSE))
            ORDER BY BI.RETURN_DATE ASC
        """
        cur2.execute(query, (today, today, student_id))
        fines = cur2.fetchall()
        
        # Convert date objects to strings
        for fine in fines:
            for key in ['ISSUE_DATE', 'RETURN_DATE', 'PAYMENT_DATE']:
                if fine.get(key):
                    fine[key] = fine[key].isoformat()
            fine['PAID'] = bool(fine['PAID']) if 'PAID' in fine else False
        
        return fk.jsonify(fines), 200
        
    except Exception as e:
        print(f"Error fetching student fines: {str(e)}")
        return fk.jsonify({'error': str(e)}), 500

@app.route('/process_fine_payment', methods=['POST'])
def process_fine_payment():
    try:
        data = fk.request.get_json()
        fine_id = data.get('fine_id')
        transaction_id = data.get('transaction_id')
        amount = data.get('amount')
        
        if not fine_id or not transaction_id:
            return fk.jsonify({'error': 'Missing required fields'}), 400
        
        # Update fine record
        cur.execute("""
            UPDATE FINE 
            SET PAID = TRUE, 
                TRANSACTION_ID = %s
                
            WHERE FINE_ID = %s
        """, (transaction_id, fine_id))
        
        if cur.rowcount == 1:
            con.commit()
            return fk.jsonify({'status': 'success'}), 200
        else:
            return fk.jsonify({'error': 'Fine not found'}), 404
            
    except Exception as e:
        con.rollback()
        print(f"Error processing payment: {str(e)}")
        return fk.jsonify({'error': str(e)}), 500

@app.route('/student_fine_history/<int:student_id>', methods=['GET'])
def get_student_fine_history(student_id):
    try:
        query = """
            SELECT 
                F.FINE_ID,
                B.TITLE,
                B.BOOK_ID,
                F.DUE_DATE,
                F.RETURN_DATE,
                F.FINE_AMOUNT,
                F.PAID,
                F.TRANSACTION_ID,
                F.PAYMENT_DATE,
                F.REASON,
                (SELECT FINE FROM LDEFAULT LIMIT 1) AS DAILY_RATE,
                DATEDIFF(F.RETURN_DATE, F.DUE_DATE) AS DAYS_OVERDUE
            FROM FINE F
            JOIN BOOKS B ON F.BOOK_ID = B.BOOK_ID
            WHERE F.STUDENT_ID = %s
            ORDER BY F.RETURN_DATE DESC
        """
        cur2.execute(query, (student_id,))
        history = cur2.fetchall()
        
        for item in history:
            for key in ['DUE_DATE', 'RETURN_DATE', 'PAYMENT_DATE']:
                if item.get(key):
                    item[key] = item[key].isoformat()
            item['PAID'] = bool(item['PAID'])
        
        return fk.jsonify(history), 200
        
    except Exception as e:
        print(f"Error fetching fine history: {str(e)}")
        return fk.jsonify({'error': str(e)}), 500
@app.route('/get_fine_history', methods=['GET'])
def get_fine_history():
    try:
        # Get filter parameters from request
        status_filter = fk.request.args.get('status', 'all')
        date_filter = fk.request.args.get('date', None)
        
        # Get student ID from session (you'll need to implement your session management)
        student_id = get_student_id_from_session()  # Replace with your actual session handling
        
        # Base query
        query = """
            SELECT 
                f.fine_id,
                b.book_id AS BOOK_ID,
                b.title AS TITLE,
                f.fine_date AS FINE_DATE,
                f.amount AS AMOUNT,
                f.payment_date AS PAYMENT_DATE,
                f.status AS STATUS,
                f.transaction_id AS TRANSACTION_ID,
                f.receipt_id AS RECEIPT_ID,
                f.reason AS REASON
            FROM fines f
            JOIN books b ON f.book_id = b.book_id
            WHERE f.student_id = %s
        """
        
        params = [student_id]
        
        # Add status filter
        if status_filter != 'all':
            if status_filter == 'Paid':
                query += " AND f.status = 'Paid'"
            elif status_filter == 'Cancelled':
                query += " AND f.status = 'Cancelled'"
        
        # Add date filter
        if date_filter:
            query += " AND f.fine_date >= %s"
            params.append(date_filter)
        
        # Order by fine date descending
        query += " ORDER BY f.fine_date DESC"
        
        cur.execute(query, params)
        fine_history = cur.fetchall()
        
        cur.close()
        con.close()
        
        # Format dates and prepare response
        formatted_history = []
        for fine in fine_history:
            formatted_fine = {
                'FINE_ID': fine['fine_id'],
                'BOOK_ID': fine['BOOK_ID'],
                'TITLE': fine['TITLE'],
                'FINE_DATE': fine['FINE_DATE'].strftime('%Y-%m-%d') if fine['FINE_DATE'] else None,
                'AMOUNT': fine['AMOUNT'],
                'PAYMENT_DATE': fine['PAYMENT_DATE'].strftime('%Y-%m-%d') if fine['PAYMENT_DATE'] else None,
                'STATUS': fine['STATUS'],
                'RECEIPT_ID': fine['RECEIPT_ID'],
                'REASON': fine['REASON']
            }
            formatted_history.append(formatted_fine)
        
        return fk.jsonify(formatted_history)
        
    except Exception as e:
        print(f"Error fetching fine history: {str(e)}")
        return fk.jsonify({'error': 'Failed to fetch fine history'}), 500

def get_student_id_from_session():
    """Replace this with your actual session management code"""
    # Example: return session.get('student_id')
    return 1  # For testing purpose
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
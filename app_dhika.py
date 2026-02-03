from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os

appDhika = Flask(__name__)
appDhika.config['SECRET_KEY'] = 'dhika2024smkn2cimahi'
appDhika.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bk_dhika.db'
appDhika.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

dbDhika = SQLAlchemy(appDhika)

class UserDhika(dbDhika.Model):
    idDhika = dbDhika.Column(dbDhika.Integer, primary_key=True)
    usernameDhika = dbDhika.Column(dbDhika.String(100), unique=True, nullable=False)
    passwordDhika = dbDhika.Column(dbDhika.String(200), nullable=False)
    namaDhika = dbDhika.Column(dbDhika.String(100), nullable=False)
    emailDhika = dbDhika.Column(dbDhika.String(100))
    roleDhika = dbDhika.Column(dbDhika.String(20), nullable=False)
    fotoDhika = dbDhika.Column(dbDhika.String(200), default='default.jpg')
    createdDhika = dbDhika.Column(dbDhika.DateTime, default=datetime.utcnow)

class KonselingDhika(dbDhika.Model):
    idDhika = dbDhika.Column(dbDhika.Integer, primary_key=True)
    siswaIdDhika = dbDhika.Column(dbDhika.Integer, dbDhika.ForeignKey('user_dhika.idDhika'))
    guruIdDhika = dbDhika.Column(dbDhika.Integer, dbDhika.ForeignKey('user_dhika.idDhika'))
    jenisDhika = dbDhika.Column(dbDhika.String(50))
    tanggalDhika = dbDhika.Column(dbDhika.DateTime)
    statusDhika = dbDhika.Column(dbDhika.String(20), default='pending')
    keteranganDhika = dbDhika.Column(dbDhika.Text)
    catatanDhika = dbDhika.Column(dbDhika.Text)
    createdDhika = dbDhika.Column(dbDhika.DateTime, default=datetime.utcnow)

class ChatDhika(dbDhika.Model):
    idDhika = dbDhika.Column(dbDhika.Integer, primary_key=True)
    pengirimIdDhika = dbDhika.Column(dbDhika.Integer, dbDhika.ForeignKey('user_dhika.idDhika'))
    penerimaIdDhika = dbDhika.Column(dbDhika.Integer, dbDhika.ForeignKey('user_dhika.idDhika'))
    pesanDhika = dbDhika.Column(dbDhika.Text, nullable=False)
    waktuDhika = dbDhika.Column(dbDhika.DateTime, default=datetime.utcnow)
    terbacaDhika = dbDhika.Column(dbDhika.Boolean, default=False)

class NotifikasiDhika(dbDhika.Model):
    idDhika = dbDhika.Column(dbDhika.Integer, primary_key=True)
    userIdDhika = dbDhika.Column(dbDhika.Integer, dbDhika.ForeignKey('user_dhika.idDhika'))
    judulDhika = dbDhika.Column(dbDhika.String(200))
    pesanDhika = dbDhika.Column(dbDhika.Text)
    terbacaDhika = dbDhika.Column(dbDhika.Boolean, default=False)
    waktuDhika = dbDhika.Column(dbDhika.DateTime, default=datetime.utcnow)

def login_required_dhika(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id_dhika' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('loginDhika'))
        return f(*args, **kwargs)
    return decorated_function

def role_required_dhika(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role_dhika') != role:
                flash('Akses ditolak', 'danger')
                return redirect(url_for('dashboardDhika'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@appDhika.route('/')
def indexDhika():
    if 'user_id_dhika' in session:
        return redirect(url_for('dashboardDhika'))
    return redirect(url_for('loginDhika'))

@appDhika.route('/login', methods=['GET', 'POST'])
def loginDhika():
    if request.method == 'POST':
        usernameDhika = request.form.get('username')
        passwordDhika = request.form.get('password')
        
        userDhika = UserDhika.query.filter_by(usernameDhika=usernameDhika).first()
        
        if userDhika and check_password_hash(userDhika.passwordDhika, passwordDhika):
            session['user_id_dhika'] = userDhika.idDhika
            session['nama_dhika'] = userDhika.namaDhika
            session['role_dhika'] = userDhika.roleDhika
            flash(f'Selamat datang, {userDhika.namaDhika}!', 'success')
            return redirect(url_for('dashboardDhika'))
        else:
            flash('Username atau password salah', 'danger')
    
    return render_template('login_dhika.html')

@appDhika.route('/logout')
def logoutDhika():
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('loginDhika'))

@appDhika.route('/dashboard')
@login_required_dhika
def dashboardDhika():
    roleDhika = session.get('role_dhika')
    userIdDhika = session.get('user_id_dhika')
    
    if roleDhika == 'siswa':
        konselingDhika = KonselingDhika.query.filter_by(siswaIdDhika=userIdDhika).order_by(KonselingDhika.createdDhika.desc()).limit(5).all()
        totalKonselingDhika = KonselingDhika.query.filter_by(siswaIdDhika=userIdDhika).count()
        pendingDhika = KonselingDhika.query.filter_by(siswaIdDhika=userIdDhika, statusDhika='pending').count()
        
        return render_template('dashboard_siswa_dhika.html', 
                             konseling=konselingDhika,
                             total=totalKonselingDhika,
                             pending=pendingDhika)
    
    elif roleDhika == 'guru_bk':
        konselingDhika = KonselingDhika.query.filter_by(guruIdDhika=userIdDhika).order_by(KonselingDhika.tanggalDhika.desc()).limit(5).all()
        pendingDhika = KonselingDhika.query.filter_by(guruIdDhika=userIdDhika, statusDhika='pending').count()
        hariIniDhika = KonselingDhika.query.filter_by(guruIdDhika=userIdDhika, statusDhika='disetujui').filter(
            dbDhika.func.date(KonselingDhika.tanggalDhika) == datetime.now().date()
        ).count()
        
        return render_template('dashboard_guru_dhika.html',
                             konseling=konselingDhika,
                             pending=pendingDhika,
                             hari_ini=hariIniDhika)
    
    elif roleDhika == 'admin':
        totalSiswaDhika = UserDhika.query.filter_by(roleDhika='siswa').count()
        totalGuruDhika = UserDhika.query.filter_by(roleDhika='guru_bk').count()
        totalKonselingDhika = KonselingDhika.query.count()
        siswaBaruDhika = UserDhika.query.filter_by(roleDhika='siswa').filter(dbDhika.func.date(UserDhika.createdDhika) == datetime.now().date()).count()
        konselingBerhasilDhika = KonselingDhika.query.filter_by(statusDhika='selesai').count()
        konselingAktifDhika = KonselingDhika.query.filter(KonselingDhika.statusDhika.in_(['pending','disetujui'])).count()
        persentaseAktifDhika = 0
        if totalKonselingDhika > 0:
            persentaseAktifDhika = int((konselingAktifDhika / totalKonselingDhika) * 100)
        aktivitasTerbaruDhika = []
        # Konseling baru diajukan
        konselingBaruList = KonselingDhika.query.order_by(KonselingDhika.createdDhika.desc()).limit(3).all()
        for k in konselingBaruList:
            aktivitasTerbaruDhika.append({
                'icon': 'calendar-plus',
                'type': 'konseling',
                'title': 'Konseling Baru Diajukan',
                'desc': f"{UserDhika.query.get(k.siswaIdDhika).namaDhika} mengajukan konseling {k.jenisDhika}",
                'waktu': k.createdDhika
            })
        # Konseling selesai
        konselingSelesaiList = KonselingDhika.query.filter_by(statusDhika='selesai').order_by(KonselingDhika.createdDhika.desc()).limit(2).all()
        for k in konselingSelesaiList:
            aktivitasTerbaruDhika.append({
                'icon': 'check-circle',
                'type': 'konseling',
                'title': 'Konseling Selesai',
                'desc': f"Guru BK menyelesaikan sesi dengan {UserDhika.query.get(k.siswaIdDhika).namaDhika}",
                'waktu': k.createdDhika
            })
        # User baru ditambahkan
        userBaruList = UserDhika.query.order_by(UserDhika.createdDhika.desc()).filter(UserDhika.createdDhika >= datetime.now() - timedelta(hours=24)).limit(2).all()
        for u in userBaruList:
            aktivitasTerbaruDhika.append({
                'icon': 'user-plus',
                'type': 'user',
                'title': 'User Baru Ditambahkan',
                'desc': f"{u.roleDhika.title()} baru: {u.namaDhika}",
                'waktu': u.createdDhika
            })
        # Urutkan aktivitas berdasarkan waktu terbaru
        aktivitasTerbaruDhika = sorted(aktivitasTerbaruDhika, key=lambda x: x['waktu'], reverse=True)[:6]
        return render_template('dashboard_admin_dhika.html',
                             total_siswa=totalSiswaDhika,
                             total_guru=totalGuruDhika,
                             total_konseling=totalKonselingDhika,
                             siswa_baru=siswaBaruDhika,
                             konseling_berhasil=konselingBerhasilDhika,
                             persentase_aktif=persentaseAktifDhika,
                             aktivitas_terbaru=aktivitasTerbaruDhika)
    
    return redirect(url_for('loginDhika'))

@appDhika.route('/konseling/ajukan', methods=['GET', 'POST'])
@login_required_dhika
def ajukanKonselingDhika():
    if request.method == 'POST':
        jenisDhika = request.form.get('jenis')
        guruIdDhika = request.form.get('guru_id')
        tanggalDhika = request.form.get('tanggal')
        jamDhika = request.form.get('jam')
        keteranganDhika = request.form.get('keterangan')
        
        tanggalWaktuDhika = datetime.strptime(f"{tanggalDhika} {jamDhika}", "%Y-%m-%d %H:%M")
        
        konselingBaru = KonselingDhika(
            siswaIdDhika=session.get('user_id_dhika'),
            guruIdDhika=guruIdDhika,
            jenisDhika=jenisDhika,
            tanggalDhika=tanggalWaktuDhika,
            keteranganDhika=keteranganDhika
        )
        
        dbDhika.session.add(konselingBaru)
        dbDhika.session.commit()
        
        notifDhika = NotifikasiDhika(
            userIdDhika=guruIdDhika,
            judulDhika='Permintaan Konseling Baru',
            pesanDhika=f'Ada permintaan konseling baru dari {session.get("nama_dhika")}'
        )
        dbDhika.session.add(notifDhika)
        dbDhika.session.commit()
        
        flash('Permintaan konseling berhasil diajukan', 'success')
        return redirect(url_for('dashboardDhika'))
    
    guruListDhika = UserDhika.query.filter_by(roleDhika='guru_bk').all()
    return render_template('ajukan_konseling_dhika.html', guru_list=guruListDhika)

@appDhika.route('/konseling/kelola')
@login_required_dhika
@role_required_dhika('guru_bk')
def kelolaKonselingDhika():
    konselingListDhika = KonselingDhika.query.filter_by(guruIdDhika=session.get('user_id_dhika')).order_by(KonselingDhika.createdDhika.desc()).all()
    return render_template('kelola_konseling_dhika.html', konseling_list=konselingListDhika)

@appDhika.route('/konseling/update/<int:id>', methods=['POST'])
@login_required_dhika
@role_required_dhika('guru_bk')
def updateKonselingDhika(id):
    konselingDhika = KonselingDhika.query.get_or_404(id)
    statusDhika = request.form.get('status')
    catatanDhika = request.form.get('catatan')
    
    konselingDhika.statusDhika = statusDhika
    if catatanDhika:
        konselingDhika.catatanDhika = catatanDhika
    
    dbDhika.session.commit()
    
    notifDhika = NotifikasiDhika(
        userIdDhika=konselingDhika.siswaIdDhika,
        judulDhika='Update Konseling',
        pesanDhika=f'Status konseling Anda telah diupdate menjadi: {statusDhika}'
    )
    dbDhika.session.add(notifDhika)
    dbDhika.session.commit()
    
    flash('Konseling berhasil diupdate', 'success')
    return redirect(url_for('kelolaKonselingDhika'))

@appDhika.route('/chat')
@login_required_dhika
def chatDhika():
    userIdDhika = session.get('user_id_dhika')
    roleDhika = session.get('role_dhika')
    
    if roleDhika == 'siswa':
        kontakDhika = UserDhika.query.filter_by(roleDhika='guru_bk').all()
    else:
        kontakDhika = UserDhika.query.filter_by(roleDhika='siswa').all()
    
    return render_template('chat_dhika.html', kontak_list=kontakDhika)

@appDhika.route('/chat/<int:user_id>')
@login_required_dhika
def chatDetailDhika(user_id):
    pesanListDhika = ChatDhika.query.filter(
        ((ChatDhika.pengirimIdDhika == session.get('user_id_dhika')) & (ChatDhika.penerimaIdDhika == user_id)) |
        ((ChatDhika.pengirimIdDhika == user_id) & (ChatDhika.penerimaIdDhika == session.get('user_id_dhika')))
    ).order_by(ChatDhika.waktuDhika.asc()).all()
    
    userDhika = UserDhika.query.get_or_404(user_id)
    
    return render_template('chat_detail_dhika.html', pesan_list=pesanListDhika, user=userDhika)

@appDhika.route('/chat/send', methods=['POST'])
@login_required_dhika
def sendChatDhika():
    dataDhika = request.get_json()
    
    chatBaru = ChatDhika(
        pengirimIdDhika=session.get('user_id_dhika'),
        penerimaIdDhika=dataDhika['penerima_id'],
        pesanDhika=dataDhika['pesan']
    )
    
    dbDhika.session.add(chatBaru)
    dbDhika.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Pesan terkirim'})

@appDhika.route('/notifikasi')
@login_required_dhika
def notifikasiDhika():
    notifListDhika = NotifikasiDhika.query.filter_by(userIdDhika=session.get('user_id_dhika')).order_by(NotifikasiDhika.waktuDhika.desc()).all()
    return render_template('notifikasi_dhika.html', notif_list=notifListDhika)

@appDhika.route('/users')
@login_required_dhika
@role_required_dhika('admin')
def usersManagementDhika():
    userListDhika = UserDhika.query.all()
    return render_template('users_dhika.html', user_list=userListDhika)

@appDhika.route('/users/add', methods=['POST'])
@login_required_dhika
@role_required_dhika('admin')
def addUserDhika():
    usernameDhika = request.form.get('username')
    passwordDhika = request.form.get('password')
    namaDhika = request.form.get('nama')
    emailDhika = request.form.get('email')
    roleDhika = request.form.get('role')
    
    hashedPasswordDhika = generate_password_hash(passwordDhika)
    
    userBaru = UserDhika(
        usernameDhika=usernameDhika,
        passwordDhika=hashedPasswordDhika,
        namaDhika=namaDhika,
        emailDhika=emailDhika,
        roleDhika=roleDhika
    )
    
    dbDhika.session.add(userBaru)
    dbDhika.session.commit()
    
    flash('User berhasil ditambahkan', 'success')
    return redirect(url_for('usersManagementDhika'))

def init_database_dhika():
    with appDhika.app_context():
        dbDhika.create_all()
        
        adminDhika = UserDhika.query.filter_by(roleDhika='admin').first()
        if not adminDhika:
            adminDefault = UserDhika(
                usernameDhika='admin',
                passwordDhika=generate_password_hash('admin123'),
                namaDhika='Admin Dhika',
                emailDhika='admin@smkn2cimahi.sch.id',
                roleDhika='admin'
            )
            dbDhika.session.add(adminDefault)
            dbDhika.session.commit()
            print("Admin default berhasil dibuat")

if __name__ == '__main__':
    init_database_dhika()
    appDhika.run(debug=True)
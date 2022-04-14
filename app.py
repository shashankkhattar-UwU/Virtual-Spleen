from flask import Flask, render_template, flash, redirect, url_for, request
from flask_mysqldb import MySQL
import yaml

app=Flask(__name__)

db=yaml.safe_load(open('db.yaml'))

app.config['SECRET_KEY']='BEST PROJECT'
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']

mysql=MySQL(app)

@app.route('/')
def home():
	return render_template('Home.html')


@app.route('/donors', methods=['GET', 'DELETE'])
def donors():
	cur=mysql.connection.cursor()
	cur.execute('SELECT * FROM donor')
	value = cur.fetchall()
	cur.close()
	return render_template('Donors.html', donors=value)


@app.route('/requests', methods=['GET', 'DELETE'])
def requests():
	cur=mysql.connection.cursor()
	cur.execute('SELECT * FROM reciepient')
	value = cur.fetchall()
	cur.close()
	return render_template('Requests.html', requests=value)

@app.route('/requestmatch/<id>')
def requestmatch(id=0):
    cur=mysql.connection.cursor()
    cur.execute(f'select * from reciepient where ID={id}')
    value=cur.fetchall()[0]
    cur.close()
    if value[7]:
        flash('This request has already been fulfilled', 'fail')
        return redirect(url_for('requests'))
    
    cur=mysql.connection.cursor()
    cur.execute(f'select donor.ID, donor.name, donor.blood_group, donor.age, donor.gender, donor.disease_history from donor, reciepient, compatible where donor.city=reciepient.city and reciepient.blood_group=compatible.rec_group and donor.blood_group=compatible.don_group and reciepient.ID={id} and donor.has_expired=0')
    donors=cur.fetchall()
    cur.close()
    return render_template('RequestMatch.html', donors=donors, request=value)

@app.route('/transaction/<id>')
def transaction(id=0):
    cur=mysql.connection.cursor()
    cur.execute(f'select * from transaction_Detail where transaction_id={id}')
    transaction=cur.fetchall()
    cur.close()
    if len(transaction)==0:
        return redirect(url_for('home'))
    transaction=transaction[0]
    return render_template('Transaction.html', transaction=transaction)

@app.route('/transactions')
def transactions():
    cur=mysql.connection.cursor()
    cur.execute(f'select * from transaction_detail')
    transactions=cur.fetchall()
    cur.close()
    return render_template('Transactions.html', transactions=transactions)
    
    
def createDonor(name, gender, age, city, bloodgroup, diseases):
    if len(diseases)==0:
        diseases='none'
    cur=mysql.connection.cursor()
    cur.execute(f"insert into donor (name, gender, age, city, blood_group, disease_history) values ('{name}', '{gender}', {age}, '{city}', '{bloodgroup}', '{diseases}')")
    mysql.connection.commit()
    cur.close()
    flash('Donor Registered Successfully', 'success')

@app.route('/donorform', methods=['GET', 'POST'])
def donorform():
    if request.method=='POST':
        if not request.form.get('name') or not request.form.get('gender') or not request.form.get('age') or not request.form.get('city') or not request.form.get('bloodgroup') or not request.form.get('rh'):
            flash('Invalid information', 'fail')
            return redirect(url_for('donorform'))
        createDonor(request.form.get('name'), request.form.get('gender'), request.form.get('age'), request.form.get('city'), f'{request.form.get("bloodgroup")}{request.form.get("rh")}', request.form.get("diseases"))
        return redirect(url_for('donors')) 
    cur=mysql.connection.cursor()
    cur.execute('select * from city')
    cities=cur.fetchall()
    cur.close()
    donor=("","","","","","","","","")
    return render_template('Donorform.html',action='add',donor=donor, cities=cities)


def editDonor(id, name, gender, age, city, bloodgroup, diseases):
    if len(diseases)==0:
        diseases='none'
    cur=mysql.connection.cursor()
    cur.execute(f"update donor set name='{name}', gender='{gender}', age={age}, city='{city}', blood_group='{bloodgroup}', disease_history='{diseases}' where ID={id}")
    mysql.connection.commit()
    cur.close()
    flash('Donor Updated Successfully', 'success')

@app.route('/donorform/<id>', methods=['GET', 'POST'])
def editdonorform(id=0):
    if request.method=='POST':
        if not request.form.get('name') or not request.form.get('gender') or not request.form.get('age') or not request.form.get('city') or not request.form.get('bloodgroup') or not request.form.get('rh'):
            flash('Invalid information', 'fail')
            return redirect(url_for('editdonorform', id=id))
        editDonor(id, request.form.get('name'), request.form.get('gender'), request.form.get('age'), request.form.get('city'), f'{request.form.get("bloodgroup")}{request.form.get("rh")}', request.form.get("diseases"))
        return redirect(url_for('donors'))
    cur=mysql.connection.cursor()
    num=cur.execute(f'select * from donor where ID={id}')
    if num==0:
        return redirect(url_for('donors'))
    donor=cur.fetchall()[0]
    cur.close()
    if donor[6]:
        flash('This donor has already donated blood and cannot be editted', 'fail')
        return redirect(url_for('donors'))
    cur=mysql.connection.cursor()
    cur.execute('select * from city')
    cities=cur.fetchall()
    cur.close()
    return render_template('Donorform.html',action='edit', cities=cities, donor=donor)


def editRequest(id, name, gender, age, city, bloodgroup, diseases, reason):
    if len(diseases)==0:
        diseases='none'
    cur=mysql.connection.cursor()
    cur.execute(f"update reciepient set name='{name}', gender='{gender}', age={age}, city='{city}', blood_group='{bloodgroup}', disease_history='{diseases}', reason='{reason}' where ID={id}")
    mysql.connection.commit()
    cur.close()
    flash('Request Updated Successfully', 'success')

@app.route('/requestform/<id>', methods=['GET', 'POST'])
def editrequestform(id=0):
    if request.method=='POST':
        if not request.form.get('name') or not request.form.get('gender') or not request.form.get('age') or not request.form.get('city') or not request.form.get('bloodgroup') or not request.form.get('rh'):
            flash('Invalid information', 'fail')
            return redirect(url_for('editrequestform', id=id))
        editRequest(id, request.form.get('name'), request.form.get('gender'), request.form.get('age'), request.form.get('city'), f'{request.form.get("bloodgroup")}{request.form.get("rh")}', request.form.get("diseases"), request.form.get("reason"))
        return redirect(url_for('requestmatch', id=id))
    cur=mysql.connection.cursor()
    num=cur.execute(f'select * from reciepient where ID={id}')
    if num==0:
        return redirect(url_for('requests'))
    value=cur.fetchall()[0]
    cur.close()
    if value[7]:
        flash('This request has already been fullfilled and cannot be editted', 'fail')
        return redirect(url_for('requests'))
    cur=mysql.connection.cursor()
    cur.execute('select * from city')
    cities=cur.fetchall()
    cur.close()
    return render_template('Requestform.html',action='edit', cities=cities, request=value)
    

def createRequest(name, gender, age, city, bloodgroup, diseases, reason):
    if len(diseases)==0:
        diseases='none'
    cur=mysql.connection.cursor()
    cur.execute(f"insert into reciepient (name, gender, age, city, blood_group, disease_history, reason) values ('{name}', '{gender}', {age}, '{city}', '{bloodgroup}', '{diseases}', '{reason}')")
    mysql.connection.commit()
    cur.close()
    flash('Request Registered Successfully', 'success')


@app.route('/requestform', methods=['GET', 'POST'])
def requestform():
    if request.method=='POST':
        if not request.form.get('name') or not request.form.get('gender') or not request.form.get('age') or not request.form.get('city') or not request.form.get('bloodgroup') or not request.form.get('rh') or not request.form.get('reason'):
            flash('Invalid information', 'fail')
            return redirect(url_for('requestform'))
        createRequest(request.form.get('name'), request.form.get('gender'), request.form.get('age'), request.form.get('city'), f'{request.form.get("bloodgroup")}{request.form.get("rh")}', request.form.get("diseases"), request.form.get("reason"))
        return redirect(url_for('requests')) 
    cur=mysql.connection.cursor()
    cur.execute('select * from city')
    cities=cur.fetchall()
    cur.close()
    value=("","","","","","","","","","")
    return render_template('Requestform.html',action="add", cities=cities, request=value)


@app.route('/delete/<person>/<id>')
def delete(person, id=0):
    if not person == 'donor' and not person=='reciepient':
        flash('cant delete', 'fail')
        return redirect(url_for('home'))
    
    cur=mysql.connection.cursor()
    cur.execute(f'delete from {person} where ID={id}')
    mysql.connection.commit()
    cur.close()
    flash('Deleted Successfully')
    if person == 'donor':
        return redirect(url_for('donors'))
    else:
        return redirect(url_for('requests'))

@app.route('/transactionfor/<using>/<id>')
def transactionfor(using,id=0):
    index=7
    queryId='r_id'
    cur=mysql.connection.cursor()
    if using == 'donor':
        index=6
        queryId='d_id'
    cur.execute(f'select * from {using} where ID={id}')
    value=cur.fetchall()[0]
    cur.close()
    if not value[index]:
        return redirect(url_for('requests'))
    cur=mysql.connection.cursor()
    cur.execute(f'select transaction_id from transaction where {queryId}={id}')
    t_id=cur.fetchall()[0][0]
    cur.close()
    return redirect(url_for('transaction', id=t_id))

@app.route('/createtransaction/<d_id>/<r_id>')
def createtransaction(d_id=0, r_id=0):
    cur=mysql.connection.cursor()
    cur.execute(f'select has_expired from donor where donor.ID={d_id}')
    d_done=cur.fetchall()[0][0]
    cur.close()
    cur=mysql.connection.cursor()
    cur.execute(f'select has_recieved from reciepient where reciepient.ID={r_id}')
    r_done=cur.fetchall()[0][0]
    cur.close()
    if r_done==1 or d_done==1:
        flash("Can't create this transaction!", 'fail')
        return redirect(url_for('requests'))
    cur=mysql.connection.cursor()
    cur.execute(f'call make_transaction({d_id}, {r_id})')
    cur.close()
    cur=mysql.connection.cursor()
    cur.execute(f'select transaction_id from transaction where d_id={d_id} and r_id={r_id}')
    t_id=cur.fetchall()[0][0]
    cur.close()
    return redirect(url_for('transaction', id=t_id))

if __name__ == '__main__':
    app.run(debug=False)
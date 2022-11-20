from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
from localStoragePy import localStoragePy

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=8e359033-a1c9-4643-82ef-8ac06f5107eb.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30120;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=glp92926;PWD=EG6HdcoRqEbMWRsL ", '', '')

app = Flask(__name__)
app.secret_key="abc123"

def getList():
    products = []
    sql = "SELECT * FROM PRODUCTS"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
      products.append(dictionary)
      dictionary = ibm_db.fetch_both(stmt)
    return products

def getOrders():
    orders = []
    sql = "SELECT * FROM ORDERS"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
      orders.append(dictionary)
      dictionary = ibm_db.fetch_both(stmt)
    return orders



@app.route("/logout")
def logout():
    return redirect("/")

@app.route("/addProductpage")
def addProductpage():
    return render_template('addProduct.html')


@app.route("/orderpage")
def orderpage():
    orders =  getOrders()
    return render_template('viewOrders.html', orders=orders)

@app.route('/delivery')
def delivery():
    name = session['user']
    role = session['role']
    email = session['email']
    products = getList()
    return render_template('home.html', name=name, role=role, products=products, email=email,msg = "Product Dispatched Successfull to Customer !")


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register_Page():
    return render_template('register.html')


@app.route('/home/<name>/<role>/<email>')
def home_Page(name,role,email):
    products= getList()
   
    return render_template('home.html', name=name, role=role, products=products ,email=email)

@app.route('/back')
def back():
    name = session['user']
    role = session['role']
    email = session['email']
    products = getList()
    return render_template('home.html', name=name, role=role, products=products, email=email)


@app.route('/offerproduct')
def offProduct():
    products = getList()
    return render_template('offerproduct.html', products=products)


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    pname = request.form['name']
    pimg = request.form['img']
    pprice = request.form['price']
    pcolor = request.form['color']
    pabout = request.form['about']
    poffprice = request.form['offprice']
    pcatagory = request.form['Catagory']
    pratting = request.form['ratting']
    pids = request.form['id']


    if request.method == 'POST':
        insert_sql = "INSERT INTO PRODUCTS VALUES (?,?,?,?,?,?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, pname)
        ibm_db.bind_param(prep_stmt, 2, pimg)
        ibm_db.bind_param(prep_stmt, 3, pprice)
        ibm_db.bind_param(prep_stmt, 4, pcolor)
        ibm_db.bind_param(prep_stmt, 5, pabout)
        ibm_db.bind_param(prep_stmt, 6, poffprice)
        ibm_db.bind_param(prep_stmt, 7,pcatagory )
        ibm_db.bind_param(prep_stmt, 8,pratting)
        ibm_db.bind_param(prep_stmt, 9,pids)
        ibm_db.bind_param(prep_stmt, 10, 'nul')
        ibm_db.execute(prep_stmt)
    name = session['user']
    role = session['role']
    email = session['email']
    products = getList()
    return render_template('home.html', name=name, role=role, products=products, email=email, msg="Product Added Successfully!")




@app.route('/addUser', methods=['GET', 'POST'])
def addUser():
    Fname = request.form['fname']
    Lname = request.form['lname']
    email = request.form['email']
    password = request.form['password']
    re_Password = request.form['confirm_password']
    if password == re_Password:
        if request.method == 'POST':

            sql = "SELECT * FROM USERS WHERE EMAIL =?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            print(account)
            if account:
                return render_template('login.html', msg="You are already a member, please login using your details")
            else:
                insert_sql = "INSERT INTO USERS VALUES (?,?,?,?,?)"
                prep_stmt = ibm_db.prepare(conn, insert_sql)
                ibm_db.bind_param(prep_stmt, 1, Fname)
                ibm_db.bind_param(prep_stmt, 2, Lname)
                ibm_db.bind_param(prep_stmt, 3, email)
                ibm_db.bind_param(prep_stmt, 4, password)
                ibm_db.bind_param(prep_stmt, 5, 'customer')
                ibm_db.execute(prep_stmt)
                return render_template('login.html', msg="User Registered Successfully, Please Login")
    else:
        return render_template('register.html', msg = "password Not Match")


@app.route('/main', methods=['GET', 'POST'])
def loginUser():
    email = request.form['email']
    password = request.form['password']
    if request.method == 'POST':
        sql = "SELECT * FROM USERS WHERE EMAIL=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            # session['account'] = account
            name = account['FIRST_NAME']
            role = account['ROLE']
            email = account['EMAIL']
            session['email'] = account['EMAIL']
            session['user'] = account['FIRST_NAME']
            session['role'] = account['ROLE']
            session.modified = True 
            return redirect(url_for('home_Page',name=name,role=role,email=email))
            # return render_template('home.html', user=account, msg="Login successful!",products=products)
        else:
            return render_template('login.html', msg="Incorrect Email / Password")


@app.route('/setProduct/<id>')
def viewProduct(id):
    sql = "SELECT * FROM PRODUCTS WHERE SUB1 =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)
    poduct = ibm_db.fetch_assoc(stmt)

    
    return render_template('viewProduct.html', product=poduct)


@app.route('/directBuy/<id>')
def directBuy(id):
    sql = "SELECT * FROM PRODUCTS WHERE SUB1 =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)
    product = ibm_db.fetch_assoc(stmt)
    name = product['NAME']
    img = product['IMG']
    color = product['COLOR']
    price = product['PRICE']
    user = session['user']
    email = session['email']

    insert_sql = "INSERT INTO ORDERS VALUES (?,?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, name)
    ibm_db.bind_param(prep_stmt, 2, img)
    ibm_db.bind_param(prep_stmt, 3, color)
    ibm_db.bind_param(prep_stmt, 4, price)
    ibm_db.bind_param(prep_stmt, 5, user)
    ibm_db.bind_param(prep_stmt, 6, email)
    ibm_db.execute(prep_stmt)

    products = getList()
    role = session['role']
    
    
    return render_template('home.html', products=products, role=role,msg="Order placed successfull")


@app.route('/addtocart/<id>')
def addtocart(id):
    sql = "SELECT * FROM PRODUCTS WHERE SUB1 =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)
    product = ibm_db.fetch_assoc(stmt)
    name = product['NAME']
    img = product['IMG']
    color = product['COLOR']
    price = product['PRICE']
    offPrice = product['OFFPRICE']
    i = product['SUB1']

    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append({'id':i,'name':name,'img':img,'color':color,'price':price,'offprice':offPrice})
    session.modified = True
    
    print(session['cart'])
    print(len(session['cart']))
    session['msg'] = "Product added successfully!"
    session.modified = True

    return redirect(url_for('viewProduct_', id=id))

@app.route('/setProduct_/<id>')
def viewProduct_(id):
    sql = "SELECT * FROM PRODUCTS WHERE SUB1 =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)
    poduct = ibm_db.fetch_assoc(stmt)


    return render_template('viewProduct.html', product=poduct, msg="Product Added Successfully")


@app.route('/viewCart')
def viewCart():
    products = session['cart']
    print(products[0]['name'])

    return render_template('cart.html',products=products)

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime


app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Paquete, Repartidor, Sucursal, Transporte
@app.route('/')
def bienvenida():
    return render_template('bienvenida.html')
@app.route('/login', methods=['GET', 'POST'])
def acceso_despachante():
    if request.method == 'POST':
        sucursal_id = request.form['sucursal']
        session['sucursal_id'] = sucursal_id
        return redirect(url_for('menu_despachante'))

    sucursales = Sucursal.query.order_by(Sucursal.id).all() #se ordena las sucursales por id
    return render_template('acceso_despachante.html', sucursales=sucursales)

@app.route('/menu-despachante')
def menu_despachante():
    sucursal_id = session.get('sucursal_id')#se obtiene el id de la sucursal en sesion
    if not sucursal_id:
        return redirect(url_for('acceso_despachante'))

    sucursal = Sucursal.query.get(sucursal_id)
    return render_template('menu_despachante.html', sucursal=sucursal)
@app.route('/registrar_paquete', methods=['GET', 'POST'])
def registrar_paquete():
    if request.method == 'POST':
        #se piden los datos con los form del html
        peso = request.form['peso']
        nomdestinatario = request.form['nombreDestinatario']
        dirdestinatario = request.form['direccionDestinatario']
 
        #se le agrega numero de envio unico
        last_paquete = Paquete.query.order_by(Paquete.numeroenvio.desc()).first()
        numeroenvio = 1 if not last_paquete else last_paquete.numeroenvio + 1
        nuevo_paquete = Paquete( #se agrega el paquete con el modelo paquete
            numeroenvio = numeroenvio, 
            peso=peso,
            nomdestinatario=nomdestinatario,
            dirdestinatario=dirdestinatario,
            entregado=False,
            observaciones = "ninguna",
            idsucursal=0,
            idtransporte = 0,
            idrepartidor = 0
        )

        try:#Se registra el nuevo paquete con los datos del form
            db.session.add(nuevo_paquete)
            db.session.commit()
            flash('Paquete registrado exitosamente.', 'success')
            return redirect(url_for('menu_despachante'))
        except Exception as e: #salta error si no se ingresaron bien los datos o la tabla se cargo de forma incorrecta
            db.session.rollback()
            flash(f'Error al registrar el paquete: {str(e)}', 'danger')
    sucursales = Sucursal.query.order_by(Sucursal.id).all()
    return render_template('registrar_paquete.html', sucursales=sucursales)
@app.route('/seleccionar_sucursal', methods=['GET', 'POST'])
def seleccionar_sucursal():
    if request.method == 'POST':
        sucursal_destino_id = request.form['sucursal_destino']
        return redirect(url_for('registrar_transporte', sucursal_destino_id=sucursal_destino_id))
    
    sucursales = Sucursal.query.order_by(Sucursal.id).all()
    return render_template('seleccionar_sucursal.html', sucursales=sucursales)
@app.route('/registrar_transporte', methods=['GET', 'POST'])
def registrar_transporte():
    sucursal_destino_id = request.args.get('sucursal_destino_id')
    print("sucursal_destino_id:", sucursal_destino_id)  
    if request.method == 'POST':
        paquetes_ids = request.form.getlist('paquetes')
        print("paquetes_ids:", paquetes_ids)  
        last_trans = Transporte.query.order_by(Transporte.id.desc()).first()
        ide = 1 if not last_trans else last_trans.id + 1
        last_num = Transporte.query.order_by(Transporte.numerotransporte.desc()).first()
        nume = 1 if not last_trans else last_num.numerotransporte + 1
        nuevo_transporte = Transporte(
        id=ide,
        numerotransporte = nume,
        fechahorasalida=datetime.now(),
        fechahorallegada=None,
        idsucursal=sucursal_destino_id
    )    
        try:
            db.session.add(nuevo_transporte)
            db.session.commit()
            print("Transporte registrado exitosamente.") 
            
            for paquete_id in paquetes_ids:
                paquete = Paquete.query.get(paquete_id)
                if not paquete.entregado:
                    paquete.idtransporte = ide
                    db.session.add(paquete)
            
            db.session.commit()
            flash('Transporte registrado exitosamente.', 'success')
            return redirect(url_for('menu_despachante'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el transporte: {str(e)}', 'danger')
            print("Error:", e)  
    
    sucursal = Sucursal.query.get(sucursal_destino_id)
    paquetes = Paquete.query.filter_by(idsucursal=sucursal_destino_id, entregado=0, idrepartidor=0).all()
    print("Paquetes:", paquetes)  
    
    return render_template('registrar_transporte.html', sucursal=sucursal, paquetes=paquetes, sucursal_destino_id=sucursal_destino_id)
@app.route('/registrar_llegada', methods=['GET', 'POST'])
def registrar_llegada():
    if request.method == 'POST':
        transporte_id = request.form.get('transporte')
        if transporte_id:
            try:
                transporte = Transporte.query.get(transporte_id)
                if transporte and not transporte.fechahorallegada:
                    transporte.fechahorallegada = datetime.now()
                    db.session.commit()
                    flash('Transporte registrado exitosamente.', 'success')
                else:
                    flash('Error: No se pudo registrar la llegada del transporte.', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al registrar la llegada del transporte: {str(e)}', 'danger')
                print("Error:", e)  
            return redirect(url_for('menu_despachante'))
    
    transportes = Transporte.query.filter(Transporte.fechahorallegada.is_(None)).all()
    print("Transportes:", transportes)  
    
    return render_template('registrar_llegada.html', transportes=transportes)
if __name__ == '__main__':
    app.run(debug=True)

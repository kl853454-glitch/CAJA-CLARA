
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import date

# CONFIGURACION
st.set_page_config(
    page_title="Caja Clara",
    page_icon="💰",
    layout="wide"
)

# BASE DE DATOS
conn = sqlite3.connect("caja_clara.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    tipo TEXT,
    categoria TEXT,
    descripcion TEXT,
    monto REAL
)
""")
conn.commit()

# FUNCIONES
def registrar_movimiento(fecha, tipo, categoria, descripcion, monto):
    conn.execute("""
    INSERT INTO movimientos
    (fecha, tipo, categoria, descripcion, monto)
    VALUES (?, ?, ?, ?, ?)
    """, (str(fecha), tipo, categoria, descripcion, monto))
    conn.commit()

def obtener_movimientos():
    return pd.read_sql_query(
        "SELECT * FROM movimientos ORDER BY fecha DESC, id DESC",
        conn
    )

# ENCABEZADO
st.title("💰 CAJA CLARA")
st.subheader("Sistema de gestión financiera para pequeños emprendimientos")
st.write("Controla tus ingresos, gastos y retiros personales de manera sencilla.")

# MENU
menu = st.sidebar.selectbox(
    "MENÚ PRINCIPAL",
    [
        "Panel principal",
        "Registrar ingresos",
        "Registrar gastos",
        "Retiros personales",
        "Historial",
        "Reportes"
    ]
)

df = obtener_movimientos()

# CALCULOS
ingresos = df[df["tipo"] == "Ingreso"]["monto"].sum()
gastos = df[df["tipo"] == "Gasto"]["monto"].sum()
retiros = df[df["tipo"] == "Retiro personal"]["monto"].sum()
saldo = ingresos - gastos - retiros

# PANEL PRINCIPAL
if menu == "Panel principal":

    st.header("Resumen financiero")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Ingresos", f"${ingresos:,.2f}")
    c2.metric("Gastos", f"${gastos:,.2f}")
    c3.metric("Retiros", f"${retiros:,.2f}")
    c4.metric("Saldo disponible", f"${saldo:,.2f}")

    st.divider()

    st.subheader("Últimos movimientos")

    if df.empty:
        st.info("Todavía no existen movimientos registrados.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

        resumen = df.groupby("tipo")["monto"].sum()

        fig = px.pie(
            values=resumen.values,
            names=resumen.index,
            title="Distribución financiera",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)

# REGISTRAR INGRESOS
elif menu == "Registrar ingresos":

    st.header("Registrar ingreso")

    with st.form("form_ingreso"):

        fecha = st.date_input("Fecha", date.today())
        categoria = st.selectbox(
            "Categoría",
            ["Ventas", "Servicios", "Otros ingresos"]
        )
        descripcion = st.text_input("Descripción")
        monto = st.number_input("Valor USD", min_value=0.01, step=0.50)

        enviar = st.form_submit_button("Guardar ingreso")

        if enviar:
            registrar_movimiento(
                fecha, "Ingreso", categoria, descripcion, monto
            )
            st.success("Ingreso registrado correctamente.")
            st.rerun()

# REGISTRAR GASTOS
elif menu == "Registrar gastos":

    st.header("Registrar gasto")

    with st.form("form_gasto"):

        fecha = st.date_input("Fecha", date.today())
        categoria = st.selectbox(
            "Categoría",
            [
                "Mercadería",
                "Transporte",
                "Arriendo",
                "Servicios básicos",
                "Sueldos",
                "Otros gastos"
            ]
        )
        descripcion = st.text_input("Descripción")
        monto = st.number_input("Valor USD", min_value=0.01, step=0.50)

        enviar = st.form_submit_button("Guardar gasto")

        if enviar:
            registrar_movimiento(
                fecha, "Gasto", categoria, descripcion, monto
            )
            st.success("Gasto registrado correctamente.")
            st.rerun()

# RETIROS PERSONALES
elif menu == "Retiros personales":

    st.header("Registrar retiro personal")

    with st.form("form_retiro"):

        fecha = st.date_input("Fecha", date.today())
        categoria = st.selectbox(
            "Categoría",
            ["Retiro del propietario", "Uso personal", "Otros"]
        )
        descripcion = st.text_input("Descripción")
        monto = st.number_input("Valor USD", min_value=0.01, step=0.50)

        enviar = st.form_submit_button("Guardar retiro")

        if enviar:
            registrar_movimiento(
                fecha, "Retiro personal", categoria, descripcion, monto
            )
            st.success("Retiro registrado correctamente.")
            st.rerun()

# HISTORIAL
elif menu == "Historial":

    st.header("Historial de movimientos")

    if df.empty:
        st.info("No hay registros disponibles.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            "Descargar historial CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="historial_caja_clara.csv",
            mime="text/csv"
        )

# REPORTES
elif menu == "Reportes":

    st.header("Reportes financieros")

    if df.empty:
        st.info("Registra movimientos para generar reportes.")
    else:
        st.metric("Saldo actual", f"${saldo:,.2f}")

        resumen = df.groupby("tipo")["monto"].sum().reset_index()

        fig = px.bar(
            resumen,
            x="tipo",
            y="monto",
            color="tipo",
            title="Resumen de movimientos",
            labels={
                "tipo": "Tipo de movimiento",
                "monto": "Valor USD"
            }
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Totales por categoría")

        st.dataframe(
            df.groupby(["tipo", "categoria"])["monto"]
            .sum()
            .reset_index(),
            use_container_width=True,
            hide_index=True
        )

# PIE DE PAGINA
st.divider()
st.caption(
    "Caja Clara | Prototipo académico de gestión financiera "
    "para pequeños emprendimientos."
)

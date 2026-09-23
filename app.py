import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Shoe Vault POS",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #111827, #374151);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    color: #d1d5db;
}

.product-card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.price {
    font-size: 22px;
    font-weight: bold;
}

.vip-box {
    background: white;
    padding: 30px;
    border-radius: 20px;
    border: 1px solid #ddd;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 100 SHOES
# =========================================================

brands = [
    "Nike",
    "Adidas",
    "Puma",
    "Skechers",
    "Bata",
    "Servis",
    "Reebok",
    "Converse",
    "Clarks",
    "Hush Puppies"
]

styles = [
    "Runner",
    "Trainer",
    "Classic",
    "Court",
    "Street",
    "Flex",
    "Comfort",
    "Sport",
    "Casual",
    "Pro"
]

colors_list = [
    "Black",
    "White",
    "Blue",
    "Grey",
    "Red",
    "Brown",
    "Navy",
    "Green",
    "Beige",
    "Olive"
]

products = []

for i in range(100):

    brand = brands[i % len(brands)]
    style = styles[i % len(styles)]
    color = colors_list[i % len(colors_list)]

    price = 2500 + (i * 275)

    products.append({
        "id": i + 1001,
        "name": f"{brand} {style} {i+1:03d}",
        "brand": brand,
        "category": "Men" if i % 2 == 0 else "Women",
        "color": color,
        "size": 39 + (i % 7),
        "price": price,
        "stock": 5 + (i % 20)
    })

catalog = pd.DataFrame(products)

# =========================================================
# SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "invoice_number" not in st.session_state:
    st.session_state.invoice_number = 10001

if "last_invoice" not in st.session_state:
    st.session_state.last_invoice = None

if "checkout" not in st.session_state:
    st.session_state.checkout = {}

# =========================================================
# FUNCTIONS
# =========================================================

def money(value):
    return f"Rs. {value:,.0f}"


def add_to_cart(product, quantity):

    existing = None

    for item in st.session_state.cart:

        if item["id"] == int(product["id"]):
            existing = item
            break

    if existing:

        existing["qty"] += quantity

    else:

        st.session_state.cart.append({
            "id": int(product["id"]),
            "name": product["name"],
            "size": int(product["size"]),
            "price": float(product["price"]),
            "qty": quantity
        })


def remove_from_cart(product_id):

    st.session_state.cart = [
        item
        for item in st.session_state.cart
        if item["id"] != product_id
    ]


def cart_total():

    return sum(
        item["price"] * item["qty"]
        for item in st.session_state.cart
    )


# =========================================================
# PDF BILL
# =========================================================

def create_pdf(
    invoice_number,
    customer,
    phone,
    cart,
    subtotal,
    discount,
    tax,
    total,
    payment_method,
    reference
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=25
    )

    center_style = ParagraphStyle(
        "center",
        parent=styles["Normal"],
        alignment=TA_CENTER
    )

    story = []

    # Store Header
    story.append(
        Paragraph(
            "👟 SHOE VAULT",
            title_style
        )
    )

    story.append(
        Paragraph(
            "PREMIUM FOOTWEAR STORE",
            center_style
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"""
            <b>Invoice:</b> #{invoice_number}<br/>
            <b>Date:</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}<br/>
            <b>Customer:</b> {customer}<br/>
            <b>Phone:</b> {phone if phone else '-'}
            """,
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 15))

    # Table

    table_data = [
        [
            "#",
            "Product",
            "Size",
            "Qty",
            "Unit Price",
            "Amount"
        ]
    ]

    for index, item in enumerate(cart, 1):

        amount = item["price"] * item["qty"]

        table_data.append([
            index,
            item["name"],
            item["size"],
            item["qty"],
            money(item["price"]),
            money(amount)
        ])

    table_data.extend([
        ["", "", "", "", "Subtotal", money(subtotal)],
        ["", "", "", "", "Discount", money(discount)],
        ["", "", "", "", "Tax", money(tax)],
        ["", "", "", "", "TOTAL", money(total)]
    ])

    table = Table(
        table_data,
        colWidths=[
            25,
            190,
            40,
            35,
            80,
            85
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#111827")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (2, 1),
                (-1, -1),
                "RIGHT"
            ),

            (
                "BACKGROUND",
                (0, -4),
                (-1, -1),
                colors.HexColor("#f3f4f6")
            ),

            (
                "FONTNAME",
                (-2, -1),
                (-1, -1),
                "Helvetica-Bold"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(table)

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"""
            <b>Payment Method:</b> {payment_method}<br/>
            <b>Reference:</b> {reference if reference else '-'}
            """,
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "Thank you for shopping with Shoe Vault!",
            center_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

<h1>👟 SHOE VAULT</h1>

<p>
Premium Shoe Store • POS • Billing • Payment • Inventory
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("👟 Shoe Vault")

st.sidebar.write("Store Management System")

page = st.sidebar.radio(
    "Menu",
    [
        "🛍️ Products",
        "🛒 Cart",
        "🧾 Billing",
        "💳 Payment Center",
        "📊 Dashboard"
    ]
)

st.sidebar.divider()

st.sidebar.metric(
    "Cart Items",
    sum(
        item["qty"]
        for item in st.session_state.cart
    )
)

st.sidebar.metric(
    "Cart Value",
    money(cart_total())
)

# =========================================================
# PRODUCTS
# =========================================================

if page == "🛍️ Products":

    st.header("🛍️ Shoe Collection")

    col1, col2, col3 = st.columns(3)

    with col1:

        search = st.text_input(
            "🔎 Search Shoe"
        )

    with col2:

        brand = st.selectbox(
            "Brand",
            ["All"] + brands
        )

    with col3:

        category = st.selectbox(
            "Category",
            ["All", "Men", "Women"]
        )

    view = catalog.copy()

    if search:

        view = view[
            view["name"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    if brand != "All":

        view = view[
            view["brand"] == brand
        ]

    if category != "All":

        view = view[
            view["category"] == category
        ]

    st.write(
        f"Showing **{len(view)}** shoes"
    )

    for _, product in view.iterrows():

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [3, 2, 2, 1]
            )

            with col1:

                st.markdown(
                    f"""
                    ### 👟 {product['name']}

                    **Brand:** {product['brand']}

                    **Category:** {product['category']}

                    **Color:** {product['color']}

                    **Size:** {product['size']}
                    """
                )

            with col2:

                st.markdown(
                    f"""
                    <div class="price">
                    {money(product['price'])}
                    </div>

                    Stock: {product['stock']}
                    """,
                    unsafe_allow_html=True
                )

            with col3:

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=int(product["stock"]),
                    value=1,
                    key=f"quantity_{product['id']}"
                )

            with col4:

                if st.button(
                    "Add",
                    key=f"add_{product['id']}"
                ):

                    add_to_cart(
                        product,
                        quantity
                    )

                    st.success(
                        "Added!"
                    )


# =========================================================
# CART
# =========================================================

elif page == "🛒 Cart":

    st.header("🛒 Shopping Cart")

    if not st.session_state.cart:

        st.info(
            "Your cart is empty."
        )

    else:

        for item in st.session_state.cart:

            col1, col2, col3, col4 = st.columns(
                [4, 1, 1, 1]
            )

            with col1:

                st.write(
                    f"**{item['name']}**"
                )

                st.caption(
                    f"Size: {item['size']}"
                )

            with col2:

                st.write(
                    money(item["price"])
                )

            with col3:

                new_qty = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=50,
                    value=item["qty"],
                    key=f"cart_qty_{item['id']}"
                )

                item["qty"] = new_qty

            with col4:

                if st.button(
                    "Remove",
                    key=f"remove_{item['id']}"
                ):

                    remove_from_cart(
                        item["id"]
                    )

                    st.rerun()

        st.divider()

        st.subheader(
            f"Cart Total: {money(cart_total())}"
        )


# =========================================================
# BILLING
# =========================================================

elif page == "🧾 Billing":

    st.header("🧾 VIP Billing")

    if not st.session_state.cart:

        st.warning(
            "Cart is empty."
        )

    else:

        customer = st.text_input(
            "Customer Name",
            "Walk-in Customer"
        )

        phone = st.text_input(
            "Customer Phone"
        )

        st.subheader("Order")

        rows = []

        for item in st.session_state.cart:

            rows.append({
                "Product": item["name"],
                "Size": item["size"],
                "Quantity": item["qty"],
                "Unit Price": money(item["price"]),
                "Amount": money(
                    item["price"] *
                    item["qty"]
                )
            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

        subtotal = cart_total()

        discount_percent = st.slider(
            "Discount %",
            0,
            50,
            0
        )

        discount = (
            subtotal *
            discount_percent /
            100
        )

        tax_percent = st.number_input(
            "Tax %",
            min_value=0.0,
            max_value=30.0,
            value=0.0,
            step=1.0
        )

        tax = (
            (subtotal - discount)
            * tax_percent
            / 100
        )

        total = (
            subtotal -
            discount +
            tax
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Subtotal",
            money(subtotal)
        )

        col2.metric(
            "Discount",
            money(discount)
        )

        col3.metric(
            "Tax",
            money(tax)
        )

        col4.metric(
            "TOTAL",
            money(total)
        )

        st.session_state.checkout = {
            "customer": customer,
            "phone": phone,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": total
        }

        st.success(
            "Billing information saved."
        )

        st.info(
            "اب Payment Center میں جا کر payment complete کریں۔"
        )


# =========================================================
# PAYMENT CENTER
# =========================================================

elif page == "💳 Payment Center":

    st.header("💳 Payment Center")

    if not st.session_state.cart:

        st.warning(
            "Cart is empty."
        )

    else:

        checkout = st.session_state.checkout

        if not checkout:

            st.warning(
                "پہلے Billing page پر جائیں۔"
            )

        else:

            total = checkout["total"]

            st.markdown(
                f"""
                <div class="vip-box">

                <h2>Amount Payable</h2>

                <h1>{money(total)}</h1>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.divider()

            payment = st.radio(
                "Select Payment Method",
                [
                    "Cash",
                    "JazzCash",
                    "Easypaisa",
                    "Bank Transfer",
                    "Card / Online Payment"
                ]
            )

            reference = ""

            if payment == "JazzCash":

                st.subheader(
                    "📱 JazzCash"
                )

                st.info(
                    "Demo payment screen. "
                    "Real JazzCash API integration "
                    "requires merchant credentials."
                )

                wallet = st.text_input(
                    "JazzCash Mobile Number"
                )

                reference = st.text_input(
                    "JazzCash Transaction ID"
                )

            elif payment == "Easypaisa":

                st.subheader(
                    "📱 Easypaisa"
                )

                st.info(
                    "Demo payment screen. "
                    "Real Easypaisa API integration "
                    "requires merchant credentials."
                )

                wallet = st.text_input(
                    "Easypaisa Mobile Number"
                )

                reference = st.text_input(
                    "Easypaisa Transaction ID"
                )

            elif payment == "Bank Transfer":

                reference = st.text_input(
                    "Bank Transaction ID"
                )

            elif payment == "Card / Online Payment":

                reference = st.text_input(
                    "Online Payment Reference"
                )

            else:

                reference = "CASH"

            if st.button(
                "✅ Confirm Payment & Generate VIP Bill",
                type="primary",
                use_container_width=True
            ):

                if payment != "Cash" and not reference:

                    st.error(
                        "Transaction/Reference ID درج کریں۔"
                    )

                else:

                    invoice = (
                        st.session_state.invoice_number
                    )

                    st.session_state.invoice_number += 1

                    pdf = create_pdf(
                        invoice,
                        checkout["customer"],
                        checkout["phone"],
                        st.session_state.cart,
                        checkout["subtotal"],
                        checkout["discount"],
                        checkout["tax"],
                        checkout["total"],
                        payment,
                        reference
                    )

                    st.session_state.last_invoice = {
                        "invoice": invoice,
                        "customer": checkout["customer"],
                        "total": checkout["total"],
                        "payment": payment,
                        "reference": reference,
                        "pdf": pdf.getvalue()
                    }

                    st.success(
                        f"Payment successful! Invoice #{invoice} generated."
                    )

                    st.balloons()

            # Show invoice

            invoice = st.session_state.last_invoice

            if invoice:

                st.divider()

                st.subheader(
                    f"🧾 VIP Invoice #{invoice['invoice']}"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Customer",
                    invoice["customer"]
                )

                col2.metric(
                    "Payment",
           

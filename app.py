import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Paragraph, Spacer


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Shoe Vault",
    page_icon="👟",
    layout="wide"
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: bold;
    }

    .sub-title {
        color: #666666;
        font-size: 18px;
    }

    .price {
        font-size: 22px;
        font-weight: bold;
    }

    .bill-box {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #dddddd;
        background-color: #fafafa;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PRODUCT DATABASE - 100 PRODUCTS
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

product_types = [
    "Running Shoe",
    "Sports Shoe",
    "Casual Shoe",
    "Sneaker",
    "Trainer",
    "Sandal",
    "Slipper",
    "Boot",
    "Formal Shoe",
    "Loafer"
]

colors = [
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
    product_type = product_types[i % len(product_types)]
    color = colors[i % len(colors)]

    price = 2500 + (i * 250)

    products.append(
        {
            "ID": i + 1,
            "Product": f"{brand} {product_type} {i + 1}",
            "Brand": brand,
            "Type": product_type,
            "Gender": "Men" if i % 2 == 0 else "Women",
            "Color": color,
            "Size": 39 + (i % 7),
            "Price": price,
            "Stock": 5 + (i % 15)
        }
    )

catalog = pd.DataFrame(products)


# =========================================================
# SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "invoice_number" not in st.session_state:
    st.session_state.invoice_number = 10001

if "last_bill" not in st.session_state:
    st.session_state.last_bill = None


# =========================================================
# FUNCTIONS
# =========================================================

def money(amount):
    return f"Rs. {amount:,.0f}"


def add_to_cart(product, quantity):

    product_id = int(product["ID"])

    for item in st.session_state.cart:

        if item["ID"] == product_id:

            item["Quantity"] += quantity
            return

    st.session_state.cart.append(
        {
            "ID": product_id,
            "Product": product["Product"],
            "Size": int(product["Size"]),
            "Price": float(product["Price"]),
            "Quantity": int(quantity)
        }
    )


def remove_from_cart(product_id):

    st.session_state.cart = [
        item
        for item in st.session_state.cart
        if item["ID"] != product_id
    ]


def cart_subtotal():

    return sum(
        item["Price"] * item["Quantity"]
        for item in st.session_state.cart
    )


# =========================================================
# PDF BILL
# =========================================================

def make_pdf(
    invoice_no,
    customer,
    phone,
    cart,
    subtotal,
    discount,
    tax,
    total,
    payment
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=24
    )

    center_style = ParagraphStyle(
        "CenterStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER
    )

    story = []

    story.append(
        Paragraph(
            "SHOE VAULT",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Premium Footwear Store",
            center_style
        )
    )

    story.append(
        Spacer(1, 15)
    )

    information = f"""
    <b>Invoice:</b> #{invoice_no}<br/>
    <b>Date:</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}<br/>
    <b>Customer:</b> {customer}<br/>
    <b>Phone:</b> {phone if phone else '-'}
    """

    story.append(
        Paragraph(
            information,
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    table_data = [
        [
            "#",
            "Product",
            "Size",
            "Qty",
            "Price",
            "Amount"
        ]
    ]

    for number, item in enumerate(cart, 1):

        amount = item["Price"] * item["Quantity"]

        table_data.append(
            [
                number,
                item["Product"],
                item["Size"],
                item["Quantity"],
                money(item["Price"]),
                money(amount)
            ]
        )

    table_data.append(
        ["", "", "", "", "Subtotal", money(subtotal)]
    )

    table_data.append(
        ["", "", "", "", "Discount", money(discount)]
    )

    table_data.append(
        ["", "", "", "", "Tax", money(tax)]
    )

    table_data.append(
        ["", "", "", "", "TOTAL", money(total)]
    )

    table = Table(
        table_data,
        colWidths=[25, 190, 40, 35, 80, 85]
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.black
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
            ]
        )
    )

    story.append(table)

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            f"<b>Payment Method:</b> {payment}",
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Thank you for shopping with Shoe Vault!",
            center_style
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">Shoe Vault</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Shoe Store • Shopping • Cart • Billing</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# SIDEBAR MENU
# =========================================================

st.sidebar.title("Shoe Vault")

page = st.sidebar.radio(
    "Menu",
    [
        "Store",
        "Dashboard"
    ]
)

st.sidebar.divider()

st.sidebar.metric(
    "Cart Items",
    sum(
        item["Quantity"]
        for item in st.session_state.cart
    )
)

st.sidebar.metric(
    "Cart Value",
    money(cart_subtotal())
)


# =========================================================
# STORE PAGE
# =========================================================

if page == "Store":

    st.header("Search Products")

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = st.text_input(
        "Search",
        placeholder="Search shoe, sandal, slipper, boot, Nike, Adidas..."
    )

    col1, col2 = st.columns(2)

    with col1:

        gender_filter = st.selectbox(
            "Gender",
            [
                "All",
                "Men",
                "Women"
            ]
        )

    with col2:

        type_filter = st.selectbox(
            "Product Type",
            ["All"] + product_types
        )

    # -----------------------------------------------------
    # FILTER PRODUCTS
    # -----------------------------------------------------

    result = catalog.copy()

    if search:

        search_text = search.lower()

        result = result[
            result["Product"].str.lower().str.contains(
                search_text,
                na=False
            )
            |
            result["Brand"].str.lower().str.contains(
                search_text,
                na=False
            )
            |
            result["Type"].str.lower().str.contains(
                search_text,
                na=False
            )
            |
            result["Color"].str.lower().str.contains(
                search_text,
                na=False
            )
        ]

    if gender_filter != "All":

        result = result[
            result["Gender"] == gender_filter
        ]

    if type_filter != "All":

        result = result[
            result["Type"] == type_filter
        ]

    st.write(
        f"**{len(result)} products found**"
    )

    # -----------------------------------------------------
    # PRODUCTS
    # -----------------------------------------------------

    if len(result) == 0:

        st.warning(
            "No product found. Try another search."
        )

    else:

        for _, product in result.iterrows():

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [5, 2, 2]
                )

                with col1:

                    st.subheader(
                        product["Product"]
                    )

                    st.write(
                        f"Brand: {product['Brand']}  |  "
                        f"Type: {product['Type']}"
                    )

                    st.write(
                        f"Gender: {product['Gender']}  |  "
                        f"Color: {product['Color']}  |  "
                        f"Size: {product['Size']}"
                    )

                with col2:

                    st.markdown(
                        f"""
                        <div class="price">
                        {money(product["Price"])}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.write(
                        f"Stock: {product['Stock']}"
                    )

                with col3:

                    quantity = st.number_input(
                        "Qty",
                        min_value=1,
                        max_value=int(product["Stock"]),
                        value=1,
                        key=f"qty_{product['ID']}"
                    )

                    if st.button(
                        "Add to Cart",
                        key=f"add_{product['ID']}",
                        use_container_width=True
                    ):

                        add_to_cart(
                            product,
                            quantity
                        )

                        st.success(
                            "Added to cart"
                        )

    # =====================================================
    # CART + BILL
    # =====================================================

    st.divider()

    st.header("Shopping Cart & Bill")

    if not st.session_state.cart:

        st.info(
            "Cart is empty. Search a product and click Add to Cart."
        )

    else:

        # -------------------------------------------------
        # CART TABLE
        # -------------------------------------------------

        cart_rows = []

        for item in st.session_state.cart:

            cart_rows.append(
                {
                    "Product": item["Product"],
                    "Size": item["Size"],
                    "Qty": item["Quantity"],
                    "Price": money(item["Price"]),
                    "Amount": money(
                        item["Price"] *
                        item["Quantity"]
                    )
                }
            )

        st.dataframe(
            pd.DataFrame(cart_rows),
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # REMOVE ITEMS
        # -------------------------------------------------

        st.subheader("Remove Product")

        for item in st.session_state.cart:

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                st.write(
                    f"{item['Product']} × {item['Quantity']}"
                )

            with col2:

                if st.button(
                    "Remove",
                    key=f"remove_{item['ID']}"
                ):

                    remove_from_cart(
                        item["ID"]
                    )

                    st.rerun()

        # -------------------------------------------------
        # BILL INFORMATION
        # -------------------------------------------------

        st.divider()

        st.subheader("Customer Information")

        col1, col2 = st.columns(2)

        with col1:

            customer = st.text_input(
                "Customer Name",
                value="Walk-in Customer"
            )

        with col2:

            phone = st.text_input(
                "Phone Number"
            )

        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        subtotal = cart_subtotal()

        col1, col2 = st.columns(2)

        with col1:

            discount_percent = st.number_input(
                "Discount %",
                min_value=0.0,
                max_value=50.0,
                value=0.0,
                step=1.0
            )

        with col2:

            tax_percent = st.number_input(
                "Tax %",
                min_value=0.0,
                max_value=30.0,
                value=0.0,
                step=1.0
            )

        discount = (
            subtotal *
            discount_percent /
            100
        )

        taxable_amount = (
            subtotal -
            discount
        )

        tax = (
            taxable_amount *
            tax_percent /
            100
        )

        total = (
            taxable_amount +
            tax
        )

        # -------------------------------------------------
        # BILL SUMMARY
        # -------------------------------------------------

        st.subheader("Bill Summary")

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

        # -------------------------------------------------
        # PAYMENT
        # -------------------------------------------------

        st.subheader("Payment")

        payment = st.selectbox(
            "Payment Method",
            [
                "Cash",
                "JazzCash",
                "Easypaisa",
                "Bank Transfer",
                "Card / Online Payment"
            ]
        )

        if payment == "JazzCash":

            st.info(
                "Demo JazzCash option. Real payment API "
                "requires merchant credentials."
            )

            reference = st.text_input(
                "JazzCash Transaction ID"
            )

        elif payment == "Easypaisa":

            st.info(
                "Demo Easypaisa option. Real payment API "
                "requires merchant credentials."
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
                "Payment Reference"
            )

        else:

            reference = "CASH"

        # -------------------------------------------------
        # GENERATE BILL
        # -------------------------------------------------

        if st.button(
            "Generate VIP Bill",
            type="primary",
            use_container_width=True
        ):

            if payment != "Cash" and not reference:

                st.error(
                    "Please enter the payment reference."
                )

            else:

                invoice_no = (
                    st.session_state.invoice_number
                )

                st.session_state.invoice_number += 1

                pdf_data = make_pdf(
                    invoice_no,
                    customer,
                    phone,
                    st.session_state.cart,
                    subtotal,
                    discount,
                    tax,
                    total,
                    payment
                )

                st.session_state.last_bill = {
                    "invoice": invoice_no,
                    "customer": customer,
                    "total": total,
                    "payment": payment,
                    "pdf": pdf_data
                }

                st.success(
                    f"Bill generated successfully! Invoice #{invoice_no}"
                )

        # -------------------------------------------------
        # SHOW GENERATED BILL
        # -------------------------------------------------

        if st.session_state.last_bill:

            bill = st.session_state.last_bill

            st.divider()

            st.subheader(
                f"VIP Bill #{bill['invoice']}"
            )

            st.write(
                f"Customer: **{bill['customer']}**"
            )

            st.write(
                f"Payment: **{bill['payment']}**"
            )

            st.write(
                f"Total: **{money(bill['total'])}**"
            )

            st.download_button(
                label="Download VIP Bill",
                data=bill["pdf"],
           

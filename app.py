import streamlit as st
import pandas as pd
from datetime import datetime


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Shoe Vault",
    page_icon="👟",
    layout="wide"
)


# =========================================================
# PRODUCTS
# =========================================================

brands = [
    "Nike", "Adidas", "Puma", "Skechers", "Bata",
    "Servis", "Reebok", "Converse", "Clarks", "Hush Puppies"
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
    "Black", "White", "Blue", "Grey", "Red",
    "Brown", "Navy", "Green", "Beige", "Olive"
]

products = []

for i in range(100):

    products.append({
        "ID": i + 1,
        "Product": (
            f"{brands[i % 10]} "
            f"{product_types[i % 10]} "
            f"{i + 1}"
        ),
        "Brand": brands[i % 10],
        "Type": product_types[i % 10],
        "Gender": "Men" if i % 2 == 0 else "Women",
        "Color": colors[i % 10],
        "Size": 39 + (i % 7),
        "Price": 2500 + (i * 250),
        "Stock": 5 + (i % 15)
    })

catalog = pd.DataFrame(products)


# =========================================================
# SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "invoice" not in st.session_state:
    st.session_state.invoice = 10001

if "bill" not in st.session_state:
    st.session_state.bill = None


# =========================================================
# FUNCTIONS
# =========================================================

def money(value):
    return f"Rs. {value:,.0f}"


def add_to_cart(product, quantity):

    product_id = int(product["ID"])

    for item in st.session_state.cart:

        if item["ID"] == product_id:
            item["Quantity"] += quantity
            return

    st.session_state.cart.append({
        "ID": product_id,
        "Product": product["Product"],
        "Size": int(product["Size"]),
        "Price": float(product["Price"]),
        "Quantity": int(quantity)
    })


def remove_item(product_id):

    st.session_state.cart = [
        item
        for item in st.session_state.cart
        if item["ID"] != product_id
    ]


def subtotal():

    total = 0

    for item in st.session_state.cart:

        total += (
            item["Price"] *
            item["Quantity"]
        )

    return total


# =========================================================
# HEADER
# =========================================================

st.title("👟 SHOE VAULT")

st.caption(
    "Shoe Store • Search • Shopping Cart • Billing"
)

st.divider()


# =========================================================
# SIDEBAR
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

cart_items = sum(
    item["Quantity"]
    for item in st.session_state.cart
)

st.sidebar.metric(
    "Cart Items",
    cart_items
)

st.sidebar.metric(
    "Cart Value",
    money(subtotal())
)


# =========================================================
# STORE
# =========================================================

if page == "Store":

    st.header("🔎 Search Products")

    search = st.text_input(
        "Search",
        placeholder="Nike, sandal, slipper, boot, shoe..."
    )

    col1, col2 = st.columns(2)

    with col1:

        gender = st.selectbox(
            "Gender",
            ["All", "Men", "Women"]
        )

    with col2:

        shoe_type = st.selectbox(
            "Product Type",
            ["All"] + product_types
        )

    result = catalog.copy()

    if search:

        text = search.lower()

        result = result[
            result["Product"].str.lower().str.contains(
                text,
                na=False
            )
            |
            result["Brand"].str.lower().str.contains(
                text,
                na=False
            )
            |
            result["Type"].str.lower().str.contains(
                text,
                na=False
            )
            |
            result["Color"].str.lower().str.contains(
                text,
                na=False
            )
        ]

    if gender != "All":

        result = result[
            result["Gender"] == gender
        ]

    if shoe_type != "All":

        result = result[
            result["Type"] == shoe_type
        ]

    st.write(
        f"**{len(result)} products found**"
    )


    # =====================================================
    # PRODUCTS
    # =====================================================

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
                    f"Brand: {product['Brand']}"
                )

                st.write(
                    f"Type: {product['Type']} | "
                    f"Color: {product['Color']} | "
                    f"Size: {product['Size']}"
                )

            with col2:

                st.subheader(
                    money(product["Price"])
                )

                st.write(
                    f"Stock: {product['Stock']}"
                )

            with col3:

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=int(product["Stock"]),
                    value=1,
                    key=f"quantity_{product['ID']}"
                )

                if st.button(
                    "Add to Cart",
                    key=f"add_{product['ID']}"
                ):

                    add_to_cart(
                        product,
                        quantity
                    )

                    st.success(
                        "Added to cart!"
                    )


    # =====================================================
    # BILL / CART
    # =====================================================

    st.divider()

    st.header("🛒 Cart & Bill")

    if not st.session_state.cart:

        st.info(
            "Cart is empty."
        )

    else:

        # Cart table

        rows = []

        for item in st.session_state.cart:

            rows.append({
                "Product": item["Product"],
                "Size": item["Size"],
                "Quantity": item["Quantity"],
                "Price": money(item["Price"]),
                "Amount": money(
                    item["Price"] *
                    item["Quantity"]
                )
            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )


        # Remove buttons

        st.subheader("Remove Product")

        for item in st.session_state.cart:

            col1, col2 = st.columns([5, 1])

            with col1:

                st.write(
                    f"{item['Product']} × {item['Quantity']}"
                )

            with col2:

                if st.button(
                    "Remove",
                    key=f"remove_{item['ID']}"
                ):

                    remove_item(
                        item["ID"]
                    )

                    st.rerun()


        st.divider()


        # Customer

        st.subheader(
            "Customer Information"
        )

        col1, col2 = st.columns(2)

        with col1:

            customer = st.text_input(
                "Customer Name",
                "Walk-in Customer"
            )

        with col2:

            phone = st.text_input(
                "Phone Number"
            )


        # Discount and tax

        col1, col2 = st.columns(2)

        with col1:

            discount_percent = st.number_input(
                "Discount %",
                min_value=0.0,
                max_value=50.0,
                value=0.0
            )

        with col2:

            tax_percent = st.number_input(
                "Tax %",
                min_value=0.0,
                max_value=30.0,
                value=0.0
            )


        # Calculation

        sub = subtotal()

        discount = (
            sub *
            discount_percent /
            100
        )

        after_discount = (
            sub -
            discount
        )

        tax = (
            after_discount *
            tax_percent /
            100
        )

        total = (
            after_discount +
            tax
        )


        # Summary

        st.subheader(
            "💰 Bill Summary"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Subtotal",
                money(sub)
            )

        with col2:

            st.metric(
                "Discount",
                money(discount)
            )

        with col3:

            st.metric(
                "Tax",
                money(tax)
            )

        with col4:

            st.metric(
                "TOTAL",
                money(total)
            )


        # Payment

        st.subheader(
            "💳 Payment"
        )

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
                "JazzCash selected. "
                "For real payment, API integration is required."
            )

            reference = st.text_input(
                "JazzCash Transaction ID"
            )

        elif payment == "Easypaisa":

            st.info(
                "Easypaisa selected. "
                "For real payment, API integration is required."
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


        # Generate bill

        if st.button(
            "🧾 Generate Bill",
            type="primary",
            use_container_width=True
        ):

            if payment != "Cash" and not reference:

                st.error(
                    "Please enter payment reference."
                )

            else:

                invoice_number = (
                    st.session_state.invoice
                )

                st.session_state.invoice += 1

                st.session_state.bill = {
                    "invoice": invoice_number,
                    "date": datetime.now().strftime(
                        "%d-%m-%Y %I:%M %p"
                    ),
                    "customer": customer,
                    "phone": phone,
                    "items": list(
                        st.session_state.cart
                    ),
                    "subtotal": sub,
                    "discount": discount,
                    "tax": tax,
                    "total": total,
                    "payment": payment,
                    "reference": reference
                }

                st.success(
                    f"Bill #{invoice_number} generated successfully!"
                )


        # =================================================
        # DISPLAY BILL
        # =================================================

        if st.session_state.bill:

            bill = st.session_state.bill

            st.divider()

            st.header(
                f"🧾 VIP BILL #{bill['invoice']}"
            )

            st.write(
                f"**Date:** {bill['date']}"
            )

            st.write(
                f"**Customer:** {bill['customer']}"
            )

            st.write(
                f"**Phone:** {bill['phone']}"
            )

            st.divider()

            bill_rows = []

            for item in bill["items"]:

                bill_rows.append({
                    "Product": item["Product"],
                    "Size": item["Size"],
                    "Qty": item["Quantity"],
                    "Price": money(item["Price"]),
                    "Amount": money(
                        item["Price"] *
                        item["Quantity"]
                    )
                })

            st.dataframe(
                pd.DataFrame(bill_rows),
                use_container_width=True,
                hide_index=True
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"Subtotal: **{money(bill['subtotal'])}**"
                )

                st.write(
                    f"Discount: **{money(bill['discount'])}**"
                )

                st.write(
                    f"Tax: **{money(bill['tax'])}**"
                )

            with col2:

                st.metric(
                    "FINAL TOTAL",
                    money(bill["total"])
                )

                st.write(
                    f"Payment: **{bill['payment']}**"
                )

            st.success(
                "Thank you for shopping with Shoe Vault!"
            )


# =========================================================
# DASHBOARD
# =========================================================

elif page == "Dashboard":

    st.header("📊 Dashboard")

    total_products = len(catalog)

    total_brands = catalog["Brand"].nunique()

    men = int(
        (catalog["Gender"] == "Men").sum()
    )

    women = int(
        (catalog["Gender"] == "Women").sum()
    )

    stock = int(
        catalog["Stock"].sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Products",
            total_products
        )

    with col2:

        st.metric(
            "Companies",
            total_brands
        )

    with col3:

        st.metric(
            "Men",
            men
        )

    with col4:

        st.metric(
            "Women",
            women
        )

    st.divider()

    st.metric(
        "Total Stock",
        stock
    )

    st.subheader(
        "Product Types"
    )

    type_data = (
        catalog["Type"]
        .value_counts()
        .reset_index()
    )

    type_data.columns = [
        "Product Type",
        "Count"
    ]

    st.dataframe(
        type_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Inventory"
    )

    st.dataframe(
        catalog,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.sidebar.divider()

st.sidebar.caption(
    "Shoe Vault POS"
)

st.sidebar.caption(
    "Python + Streamlit"
) 

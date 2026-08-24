import random
from datetime import datetime, timedelta

from .connection import get_connection


random.seed(42)


FIRST_NAMES = [
    "João",
    "Maria",
    "Carlos",
    "Ana",
    "Lucas",
    "Juliana",
    "Pedro",
    "Mariana",
    "Rafael",
    "Camila",
    "Gabriel",
    "Larissa",
    "Bruno",
    "Beatriz",
    "Felipe",
    "Amanda",
]

LAST_NAMES = [
    "Silva",
    "Santos",
    "Oliveira",
    "Souza",
    "Costa",
    "Pereira",
    "Rodrigues",
    "Almeida",
    "Nascimento",
    "Lima",
]


REGIONS = {
    "SP": "Sudeste",
    "RJ": "Sudeste",
    "MG": "Sudeste",
    "ES": "Sudeste",
    "PR": "Sul",
    "SC": "Sul",
    "RS": "Sul",
    "BA": "Nordeste",
    "PE": "Nordeste",
    "CE": "Nordeste",
    "GO": "Centro-Oeste",
    "DF": "Centro-Oeste",
    "MT": "Centro-Oeste",
    "PA": "Norte",
    "AM": "Norte",
}


PRODUCTS = [
    ("Notebook Pro 14", "Notebooks", 2800.00, 4299.90),
    ("Notebook Air 13", "Notebooks", 2200.00, 3499.90),
    ("Mouse Wireless", "Periféricos", 45.00, 99.90),
    ("Teclado Mecânico RGB", "Periféricos", 180.00, 349.90),
    ("Monitor 27 4K", "Monitores", 1100.00, 1899.90),
    ("Monitor 24 Full HD", "Monitores", 650.00, 999.90),
    ("Headset Gamer", "Áudio", 150.00, 299.90),
    ("Fone Bluetooth Pro", "Áudio", 220.00, 449.90),
    ("Webcam Full HD", "Periféricos", 120.00, 249.90),
    ("SSD 1TB NVMe", "Componentes", 300.00, 549.90),
    ("SSD 512GB NVMe", "Componentes", 180.00, 349.90),
    ("Memória RAM 16GB", "Componentes", 180.00, 329.90),
    ("Cadeira Ergonomica", "Móveis", 700.00, 1299.90),
    ("Suporte para Notebook", "Acessórios", 60.00, 129.90),
    ("Hub USB-C 7 em 1", "Acessórios", 90.00, 199.90),
]


def create_tables(connection):
    connection.execute("DROP TABLE IF EXISTS order_items")
    connection.execute("DROP TABLE IF EXISTS orders")
    connection.execute("DROP TABLE IF EXISTS products")
    connection.execute("DROP TABLE IF EXISTS customers")

    connection.execute(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            region VARCHAR NOT NULL,
            state VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            cost_price DECIMAL(10, 2) NOT NULL,
            selling_price DECIMAL(10, 2) NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            status VARCHAR NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL
        )
        """
    )


def generate_customers(connection, total=1000):
    customers = []

    states = list(REGIONS.keys())

    for customer_id in range(1, total + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        name = f"{first_name} {last_name}"
        email = f"customer{customer_id}@example.com"

        state = random.choice(states)
        region = REGIONS[state]

        created_at = datetime(2024, 1, 1) + timedelta(
            days=random.randint(0, 730)
        )

        customers.append(
            (
                customer_id,
                name,
                email,
                region,
                state,
                created_at,
            )
        )

    connection.executemany(
        """
        INSERT INTO customers
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        customers,
    )


def generate_products(connection):
    products = [
        (
            product_id,
            name,
            category,
            cost_price,
            selling_price,
        )
        for product_id, (
            name,
            category,
            cost_price,
            selling_price,
        ) in enumerate(PRODUCTS, start=1)
    ]

    connection.executemany(
        """
        INSERT INTO products
        VALUES (?, ?, ?, ?, ?)
        """,
        products,
    )


def generate_orders(connection, total=5000):
    orders = []

    start_date = datetime(2025, 1, 1)

    statuses = [
        "completed",
        "completed",
        "completed",
        "completed",
        "cancelled",
    ]

    for order_id in range(1, total + 1):
        customer_id = random.randint(1, 1000)

        order_date = start_date + timedelta(
            days=random.randint(0, 364)
        )

        status = random.choice(statuses)

        orders.append(
            (
                order_id,
                customer_id,
                order_date.date(),
                status,
            )
        )

    connection.executemany(
        """
        INSERT INTO orders
        VALUES (?, ?, ?, ?)
        """,
        orders,
    )


def generate_order_items(connection, total_orders=5000):
    items = []

    item_id = 1

    for order_id in range(1, total_orders + 1):
        number_of_products = random.randint(1, 4)

        product_ids = random.sample(
            range(1, len(PRODUCTS) + 1),
            number_of_products,
        )

        for product_id in product_ids:
            product = PRODUCTS[product_id - 1]

            selling_price = product[3]

            quantity = random.randint(1, 5)

            items.append(
                (
                    item_id,
                    order_id,
                    product_id,
                    quantity,
                    selling_price,
                )
            )

            item_id += 1

    connection.executemany(
        """
        INSERT INTO order_items
        VALUES (?, ?, ?, ?, ?)
        """,
        items,
    )


def main():
    connection = get_connection()

    try:
        print("Creating database tables...")
        create_tables(connection)

        print("Generating customers...")
        generate_customers(connection)

        print("Generating products...")
        generate_products(connection)

        print("Generating orders...")
        generate_orders(connection)

        print("Generating order items...")
        generate_order_items(connection)

        print("\nDatabase created successfully!")

        for table in [
            "customers",
            "products",
            "orders",
            "order_items",
        ]:
            result = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()

            print(f"{table}: {result[0]} rows")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
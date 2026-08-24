from app.database.connection import get_connection


def get_top_products(limit: int = 10):
    connection = get_connection()

    try:
        query = """
            SELECT
                p.name,
                SUM(oi.quantity) AS total_sold,
                SUM(oi.quantity * oi.unit_price) AS revenue
            FROM order_items oi
            JOIN products p
                ON p.id = oi.product_id
            JOIN orders o
                ON o.id = oi.order_id
            WHERE o.status = 'completed'
            GROUP BY p.name
            ORDER BY total_sold DESC
            LIMIT ?
        """

        return connection.execute(query, [limit]).fetchall()

    finally:
        connection.close()


def get_revenue_by_region():
    connection = get_connection()

    try:
        query = """
            SELECT
                c.region,
                SUM(
                    oi.quantity * oi.unit_price
                ) AS revenue
            FROM order_items oi
            JOIN orders o
                ON o.id = oi.order_id
            JOIN customers c
                ON c.id = o.customer_id
            WHERE o.status = 'completed'
            GROUP BY c.region
            ORDER BY revenue DESC
        """

        return connection.execute(query).fetchall()

    finally:
        connection.close()
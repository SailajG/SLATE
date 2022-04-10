from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

    @staticmethod
    def get(user_id, conn):
        cursor = conn.cursor()
        sql = "SELECT * FROM user WHERE google_id = %s"
        data = (user_id)
        cursor.execute(sql, data)
        user = cursor.fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2]
        )
        return user

    @staticmethod
    def create(id_, name, email, conn):
        cursor = conn.cursor()
        sql = "INSERT INTO user (google_id, name, email) VALUES (%s, %s, %s)"
        data = (id_, name, email)
        cursor.execute(sql, data)
        conn.commit()

    @staticmethod
    def update_user(id_, new_name, new_email, conn):
        cursor = conn.cursor()
        sql = "update user set email = %s, set name = %s where google_id = %s"
        data = (id_, new_name, new_email)
        cursor.execute(sql, data)
        conn.commit()

    @staticmethod
    def update_user_email(id_, new_email, conn):
        cursor = conn.cursor()
        sql = "update user set email = %s where google_id = %s"
        data = (id_, new_email)
        cursor.execute(sql, data)
        conn.commit()

    @staticmethod
    def delete_by_id(id_, conn):
        cursor = conn.cursor()
        sql = "delete from user google_id = %s"
        data = (id_)
        cursor.execute(sql, data)
        conn.commit()

    @staticmethod
    def delete_by_name(name, conn):
        cursor = conn.cursor()
        sql = "delete from user name = %s"
        data = (name)
        cursor.execute(sql, data)
        conn.commit()

import os
import sys
from flask import jsonify, request, Flask, session, current_app
from Models.Comment import ListToDictComment
from create_database import create_connection
from flask_cors import CORS
from Models.User import User, ListToDict
from Models.Post import Post, ListToDictPost
import json
import sqlite3
import sqlalchemy
import jwt
import security
from send_email import send_mail
from multiprocessing import Process

app = Flask(__name__)

app.config["DEBUG"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 1000
app.config["SECRET_KEY"] = "SECRET_KEY"


CORS(app)


database = create_connection("./instance/redit.db")

app.secret_key = "hhhhhh"
cursor = database.cursor()


@app.route("/home", methods=["get"])
def home():
    cursor.execute("select * from topic")
    database.commit()
    postsRAW = cursor.fetchall()
    allPosts = []

    for post in postsRAW:
        cursor.execute("select username from user WHERE id=?", (post[5],))
        database.commit()
        id = cursor.fetchone()
        allPosts.append(ListToDictPost(post, id[0]))

    return jsonify(allPosts)


@app.route("/profile", methods=["get", "post"])
def profile():
    user = security.token_required(database, app.config["SECRET_KEY"])

    return jsonify(user)


@app.route("/like", methods=["get", "post"])
def like():
    user = security.token_required(database, app.config["SECRET_KEY"])
    print("TEST1")
    id = request.get_json()
    cursor.execute("""UPDATE topic SET likes=likes+1 where id=?""", (int(id),))
    database.commit()

    liked_topic = []
    cursor.execute("""SELECT likedTopic from user where id=?""", (user["id"],))
    database.commit()
    liked_topic_JSON = cursor.fetchone()

    liked_topic = json.loads(liked_topic_JSON[0])
    liked_topic.append(id)

    cursor.execute(
        """UPDATE user SET likedTopic=? WHERE id=?""",
        (
            json.dumps(liked_topic),
            user["id"],
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/unlike", methods=["get", "post"])
def unlike():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()
    cursor.execute("""UPDATE topic SET likes=likes-1 where id=?""", (int(id),))
    database.commit()

    liked_topic = []
    cursor.execute("""SELECT likedTopic from user where id=?""", (user["id"],))
    database.commit()
    liked_topic_JSON = cursor.fetchone()

    liked_topic = json.loads(liked_topic_JSON[0])
    liked_topic.remove(id)

    cursor.execute(
        """UPDATE user SET likedTopic=? WHERE id=?""",
        (
            json.dumps(liked_topic),
            user["id"],
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/dislike", methods=["get", "post"])
def dislike():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()
    cursor.execute("""UPDATE topic SET dislikes=dislikes+1 where id=?""", (int(id),))
    database.commit()

    disliked_topic = []
    cursor.execute("""SELECT unlikedTopic from user where id=?""", (user["id"],))
    database.commit()
    disliked_topic_JSON = cursor.fetchone()

    disliked_topic = json.loads(disliked_topic_JSON[0])
    disliked_topic.append(id)

    cursor.execute(
        """UPDATE user SET unlikedTopic=? WHERE id=?""",
        (
            json.dumps(disliked_topic),
            user["id"],
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/undislike", methods=["get", "post"])
def undislike():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()
    cursor.execute("""UPDATE topic SET dislikes=dislikes-1 where id=?""", (int(id),))
    database.commit()

    disliked_topic = []
    cursor.execute("""SELECT unlikedTopic from user where id=?""", (user["id"],))
    database.commit()
    disliked_topic_JSON = cursor.fetchone()

    disliked_topic = json.loads(disliked_topic_JSON[0])
    disliked_topic.remove(id)

    cursor.execute(
        """UPDATE user SET unlikedTopic=? WHERE id=?""",
        (
            json.dumps(disliked_topic),
            user["id"],
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/change-data", methods=["get", "post"])
def changeData():
    user = security.token_required(database, app.config["SECRET_KEY"])
    user_update = request.get_json()

    if (
        user["email"] == ""
        or user["password"] == ""
        or user["address"] == ""
        or user["firstName"] == ""
        or user["lastName"] == ""
        or user["country"] == ""
        or user["username"] == ""
        or user["phoneNumber"] == ""
    ):
        return jsonify("FALSE")

    cursor.execute(
        """UPDATE user SET firstName=?,lastName=?,username=?,password=?,country=?,address=?,email=?,phoneNumber=?WHERE id=?""",
        (
            user_update["firstName"],
            user_update["lastName"],
            user_update["username"],
            user_update["password"],
            user_update["country"],
            user_update["address"],
            user_update["email"],
            user_update["phoneNumber"],
            user["id"],
        ),
    )
    database.commit()

    return jsonify("TRUE")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.get_json()
        if user["email"] == "" or user["password"] == "":
            return jsonify("FALSE")
        cursor.execute("""SELECT * from user""")
        database.commit()
        db_list = cursor.fetchall()
        userr = {}
        for i in db_list:
            if i[8] == user["email"] and i[6] == user["password"]:
                cursor.execute(
                    """UPDATE user SET loggedIn='Y'WHERE email=?""", (user["email"],)
                )
                database.commit()
                userr["token"] = jwt.encode(
                    {"id": i[0]}, app.config["SECRET_KEY"], algorithm="HS256"
                )
                return jsonify(userr)

        return jsonify("FALSE")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user = request.get_json()

        if (
            user["email"] == ""
            or user["password"] == ""
            or user["address"] == ""
            or user["firstName"] == ""
            or user["lastName"] == ""
            or user["country"] == ""
            or user["username"] == ""
            or user["phoneNumber"] == ""
        ):
            return jsonify("FALSE")

        cursor.execute("""SELECT * from user""")
        database.commit()
        db_list = cursor.fetchall()
        for i in db_list:
            if i[6] == user["password"]:
                return jsonify("Password already exist! Try different one!")

            elif i[5] == user["username"]:
                return jsonify("Username already exist! Try different one!")

        cursor.execute("SELECT COALESCE(MAX(id),0) FROM user")
        database.commit()
        oldid = cursor.fetchone()
        newid = oldid[0] + 1

        cursor.execute(
            """INSERT OR REPLACE INTO  user (id,firstName,lastName,address,country,username,password,phoneNumber,email,loggedIn,likedTopic,unlikedTopic,likedComment,unlikedComment,interests) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                newid,
                user["firstName"],
                user["lastName"],
                user["address"],
                user["country"],
                user["username"],
                user["password"],
                user["phoneNumber"],
                user["email"],
                "N",
                "[]",
                "[]",
                "[]",
                "[]",
                "[]",
            ),
        )
        database.commit()
        print("user:" + user["username"] + "  pasword:" + user["password"])
        sys.stdout.flush()
        return jsonify("Succes!")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    user = security.token_required(database, app.config["SECRET_KEY"])
    cursor.execute(
        """UPDATE user SET loggedIn='N'WHERE username=?""", (user["username"],)
    )
    database.commit()
    return jsonify("TRUE")


@app.route("/add-post", methods=["GET", "POST"])
def addpost():
    user = security.token_required(database, app.config["SECRET_KEY"])
    cursor.execute("SELECT COALESCE(MAX(id),0) FROM topic")
    database.commit()
    oldid = cursor.fetchone()
    newid = oldid[0] + 1

    newPost = request.get_json()

    cursor.execute(
        """INSERT OR REPLACE INTO  topic (id,title,description,likes,dislikes,user_id,isDeleted,isClosed,commentsNumber,subscribedUser) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            newid,
            newPost["title"],
            newPost["description"],
            newPost["likes"],
            newPost["dislikes"],
            user["id"],
            0,
            0,
            0,
            "[]",
        ),
    )
    database.commit()

    return jsonify("TRUE")


@app.route("/notify", methods=["get", "post"])
def notify():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()

    notified_topic = []
    cursor.execute("""SELECT interests from user where id=?""", (user["id"],))
    database.commit()
    notified_topic_JSON = cursor.fetchone()

    notified_topic = json.loads(notified_topic_JSON[0])
    notified_topic.append(id)

    cursor.execute(
        """UPDATE user SET interests=? WHERE id=?""",
        (
            json.dumps(notified_topic),
            user["id"],
        ),
    )
    database.commit()

    cursor.execute("""SELECT subscribedUser from topic where id=?""", (id,))
    database.commit()

    subscribed_user_JSON = cursor.fetchone()

    subscribed_user = json.loads(subscribed_user_JSON[0])
    subscribed_user.append(user["id"])

    cursor.execute(
        """UPDATE topic SET subscribedUser=? WHERE id=?""",
        (
            json.dumps(subscribed_user),
            id,
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/unnotify", methods=["get", "post"])
def unnotify():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()

    notified_topic = []
    cursor.execute("""SELECT interests from user where id=?""", (user["id"],))
    database.commit()
    notified_topic_JSON = cursor.fetchone()

    notified_topic = json.loads(notified_topic_JSON[0])
    notified_topic.remove(id)

    cursor.execute(
        """UPDATE user SET interests=? WHERE id=?""",
        (
            json.dumps(notified_topic),
            user["id"],
        ),
    )
    database.commit()

    cursor.execute("""SELECT subscribedUser from topic where id=?""", (id,))
    database.commit()

    subscribed_user_JSON = cursor.fetchone()

    subscribed_user = json.loads(subscribed_user_JSON[0])
    subscribed_user.remove(user["id"])

    cursor.execute(
        """UPDATE topic SET subscribedUser=? WHERE id=?""",
        (
            json.dumps(subscribed_user),
            id,
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/add-comment", methods=["get", "post"])
def addcomment():
    if request.method == "GET":
        print("getttt")
        cursor.execute("select * from comment")
        database.commit()
        commentsRAW = cursor.fetchall()
        allComments = []

        for comment in commentsRAW:
            cursor.execute("select username from user WHERE id=?", (comment[4],))
            database.commit()
            id = cursor.fetchone()
            allComments.append(ListToDictComment(comment, id[0]))

        return jsonify(allComments)

    if request.method == "POST":
        print("usepsno")
        user = security.token_required(database, app.config["SECRET_KEY"])
        newComment = request.get_json()
        print(newComment)
        cursor.execute("SELECT COALESCE(MAX(id),0) FROM comment")
        database.commit()
        oldid = cursor.fetchone()
        newid = oldid[0] + 1

        cursor.execute(
            """INSERT OR REPLACE INTO  comment (id,desc,likes,dislikes,user_id,topic_id) VALUES (?,?,?,?,?,?)""",
            (
                newid,
                newComment["desc"],
                newComment["likes"],
                newComment["dislikes"],
                user["id"],
                newComment["topic_id"],
            ),
        )
        database.commit()

        cursor.execute(
            """select title from topic where id=?""", (newComment["topic_id"],)
        )
        database.commit()

        tema = cursor.fetchone()[0]

        cursor.execute(
            """UPDATE topic set commentsNumber=commentsNumber+1 where id=?""",
            (newComment["topic_id"],),
        )
        database.commit()

        cursor.execute(
            """select subscribedUser from topic where id=?""", (newComment["topic_id"],)
        )
        database.commit()

        subscribed_user_JSON = cursor.fetchone()

        subscribed_user = json.loads(subscribed_user_JSON[0])
        print(subscribed_user)
        subscribed_user1 = ",".join(map(str, subscribed_user))
        print(subscribed_user1)

        cursor.execute("select email from user where id in (%s)" % (subscribed_user1))
        database.commit()

        temp = cursor.fetchall()
        emails = []
        for row in temp:
            emails.append(row[0])

        # for element in emails:
        p1 = Process(
            target=send_mail,
            args=(emails, user["username"], newComment["desc"], tema, newid),
        )
        p1.start()

        return jsonify("TRUE")


# COMMENT


@app.route("/likeComment", methods=["get", "post"])
def likeComment():
    user = security.token_required(database, app.config["SECRET_KEY"])
    print("TEST1")
    id = request.get_json()
    cursor.execute("""UPDATE comment SET likes=likes+1 where id=?""", (int(id),))
    database.commit()

    liked_comment = []
    cursor.execute("""SELECT likedComment from user where id=?""", (user["id"],))
    database.commit()
    liked_comment_JSON = cursor.fetchone()

    liked_comment = json.loads(liked_comment_JSON[0])
    liked_comment.append(id)

    cursor.execute(
        """UPDATE user SET likedComment=? WHERE id=?""",
        (
            json.dumps(liked_comment),
            user["id"],
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/likeCommentEmail/<int:idComment>/<string:email>", methods=["get", "post"])
def likeCommentEmail(idComment, email):
    liked_comment = []
    cursor.execute("""SELECT likedComment from user where email=?""", (email,))
    database.commit()

    liked_comment_Email_JSON = cursor.fetchone()
    liked_comment = json.loads(liked_comment_Email_JSON[0])

    if idComment in liked_comment:
        return jsonify("False: Comment is already liked")

    liked_comment.append(idComment)

    cursor.execute(
        """UPDATE user SET likedComment=? WHERE email=?""",
        (
            json.dumps(liked_comment),
            email,
        ),
    )
    database.commit()

    cursor.execute("""UPDATE comment SET likes=likes+1 where id=?""", (idComment,))
    database.commit()

    # UNLIKEDDDDDDDD

    unliked_comment = []
    cursor.execute("""SELECT unlikedComment from user where email=?""", (email,))
    database.commit()

    unliked_comment_Email_JSON = cursor.fetchone()
    unliked_comment = json.loads(unliked_comment_Email_JSON[0])

    if idComment in unliked_comment:
        unliked_comment.remove(idComment)

        cursor.execute(
            """UPDATE user SET unlikedComment=? WHERE email=?""",
            (
                json.dumps(unliked_comment),
                email,
            ),
        )
        database.commit()

        cursor.execute(
            """UPDATE comment SET dislikes=dislikes-1 where id=?""", (idComment,)
        )
        database.commit()

    return jsonify("Comment successfully liked")


@app.route(
    "/dislikeCommentEmail/<int:idComment>/<string:email>", methods=["get", "post"]
)
def dislikeCommentEmail(idComment, email):
    disliked_comment = []
    cursor.execute("""SELECT unlikedComment from user where email=?""", (email,))
    database.commit()

    disliked_comment_Email_JSON = cursor.fetchone()
    disliked_comment = json.loads(disliked_comment_Email_JSON[0])

    if idComment in disliked_comment:
        return jsonify("False: Comment is already disliked")

    disliked_comment.append(idComment)

    cursor.execute(
        """UPDATE user SET unlikedComment=? WHERE email=?""",
        (
            json.dumps(disliked_comment),
            email,
        ),
    )
    database.commit()

    cursor.execute(
        """UPDATE comment SET dislikes=dislikes+1 where id=?""", (idComment,)
    )
    database.commit()

    # UNLIKEDDDDDDDD

    liked_comment = []
    cursor.execute("""SELECT likedComment from user where email=?""", (email,))
    database.commit()

    liked_comment_Email_JSON = cursor.fetchone()
    liked_comment = json.loads(liked_comment_Email_JSON[0])

    if idComment in liked_comment:
        liked_comment.remove(idComment)

        cursor.execute(
            """UPDATE user SET likedComment=? WHERE email=?""",
            (
                json.dumps(liked_comment),
                email,
            ),
        )
        database.commit()

        cursor.execute("""UPDATE comment SET likes=likes-1 where id=?""", (idComment,))
        database.commit()

    return jsonify("Comment successfully disliked")


@app.route("/unlikeComment", methods=["get", "post"])
def unlikeComment():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()
    cursor.execute("""UPDATE comment SET likes=likes-1 where id=?""", (int(id),))
    database.commit()

    liked_comment = []
    cursor.execute("""SELECT likedComment from user where id=?""", (user["id"],))
    database.commit()
    liked_comment_JSON = cursor.fetchone()

    liked_comment = json.loads(liked_comment_JSON[0])
    liked_comment.remove(id)

    cursor.execute(
        """UPDATE user SET likedComment=? WHERE id=?""",
        (
            json.dumps(liked_comment),
            user["id"],
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/dislikeComment", methods=["get", "post"])
def dislikeComment():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()
    cursor.execute("""UPDATE comment SET dislikes=dislikes+1 where id=?""", (int(id),))
    database.commit()

    disliked_comment = []
    cursor.execute("""SELECT unlikedComment from user where id=?""", (user["id"],))
    database.commit()
    disliked_comment_JSON = cursor.fetchone()

    disliked_comment = json.loads(disliked_comment_JSON[0])
    disliked_comment.append(id)

    cursor.execute(
        """UPDATE user SET unlikedComment=? WHERE id=?""",
        (
            json.dumps(disliked_comment),
            user["id"],
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/undislikeComment", methods=["get", "post"])
def undislikeComment():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()
    cursor.execute("""UPDATE comment SET dislikes=dislikes-1 where id=?""", (int(id),))
    database.commit()

    disliked_comment = []
    cursor.execute("""SELECT unlikedComment from user where id=?""", (user["id"],))
    database.commit()
    disliked_comment_JSON = cursor.fetchone()

    disliked_comment = json.loads(disliked_comment_JSON[0])
    disliked_comment.remove(id)

    cursor.execute(
        """UPDATE user SET unlikedComment=? WHERE id=?""",
        (
            json.dumps(disliked_comment),
            user["id"],
        ),
    )
    database.commit()

    return jsonify(user)


@app.route("/deletePost", methods=["get", "post"])
def deletePost():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()
    cursor.execute("""UPDATE topic SET isDeleted=1 where id=?""", (int(id),))
    database.commit()

    return jsonify("TRUE")


@app.route("/openClosePost", methods=["get", "post"])
def openClosePost():
    user = security.token_required(database, app.config["SECRET_KEY"])

    id = request.get_json()

    cursor.execute("""Select isClosed from topic where id=?""", (int(id),))
    database.commit()
    isClosed = cursor.fetchone()
    isClosed = isClosed[0]

    if isClosed == 0:
        isClosed = 1
    else:
        isClosed = 0

    cursor.execute(
        """UPDATE topic SET isClosed=? where id=?""",
        (
            isClosed,
            int(id),
        ),
    )
    database.commit()

    return jsonify("TRUE")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

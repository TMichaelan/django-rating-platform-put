import csv
import mysql.connector

def load_data_from_csv():
    cnx = mysql.connector.connect(user='root', password='', database='userview')
    cursor = cnx.cursor()
    
    with open('movies.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            genres = [genre.strip() for genre in row['Genre'].split(',')]
            
            # Insert movie
            movie_insert_query = (
                "INSERT INTO userview_movie (imdb_url, title, year, img_url)"
                "VALUES (%s, %s, %s, %s)"
            )
            movie_data = (row['IMDBID'], row['Title'], int(row['Year']), row['URL'])
            cursor.execute(movie_insert_query, movie_data)
            movie_id = cursor.lastrowid
            
            # Insert genres and make relation to movie
            for genre in genres:
                genre_select_query = "SELECT id FROM userview_genre WHERE name = %s"
                cursor.execute(genre_select_query, (genre,))
                result = cursor.fetchone()
                if result:
                    genre_id = result[0]
                else:
                    genre_insert_query = (
                        "INSERT INTO userview_genre (name)"
                        "VALUES (%s)"
                    )
                    cursor.execute(genre_insert_query, (genre,))
                    genre_id = cursor.lastrowid
                
                relation_insert_query = (
                    "INSERT INTO userview_movie_genres (movie_id, genre_id)"
                    "VALUES (%s, %s)"
                )
                cursor.execute(relation_insert_query, (movie_id, genre_id))
                
            # Insert ratings
            ratings_insert_query = (
                "INSERT INTO userview_imdbrating (audience_rating, critic_rating, movie_id)"
                "VALUES (%s, %s, %s)"
            )
            ratings_data = (float(row['Audience_Rating']), float(row['Critic_Rating']), movie_id)
            cursor.execute(ratings_insert_query, ratings_data)
            
            # Insert comment
            # Here we assume that there is a user with id 1 who made the comments
            comment_insert_query = (
                "INSERT INTO userview_comment (user_review, user_id, movie_id, timestamp)"
                "VALUES (%s, %s, %s, NOW())"
            )
            comment_data = (row['User_Review'], 1, movie_id)
            cursor.execute(comment_insert_query, comment_data)
            
    cnx.commit()
    cursor.close()
    cnx.close()

load_data_from_csv()

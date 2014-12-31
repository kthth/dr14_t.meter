# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011  Simone Riva
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3 
import threading

from dr14tmeter.dr14_config import get_db_path

unique_db_object = 0 ;
lock_db = threading.Lock()


class dr_database :
    
    def __init__(self):
        
        global unique_db_object
        global lock_db
        
        lock_db.acquire()
        if unique_db_object > 0 :
            lock_db.release()
            raise Exception("Error: database.dr_database.__init__ database is not unique !")
        
        unique_db_object = 1
        lock_db.release()
        
        self._insert_session = False

        self._tracks = {}
        self._albums = {}
        self._artists = {}
        self._genre = {}
        self._codec = {} 
        self._dr = {}
        self._date = {}
        
        self._id_artist = 0
        self._id_album = 0
        self._id_track = 0
        self._id_genre = 0
        self._id_codec = 0
        self._id_dr = 0
        self._id_date = 0 
    
    
    def build_database(self):
        global lock_db
        lock_db.acquire()
        if self._insert_session :
            lock_db.release()
            raise Exception("Error: database.build_database It's impossible to build the database during an insertion !")        
        db = self.dr14_db_main_structure_v1()
        
        conn = sqlite3.connect( get_db_path() )
        
        conn.executescript( db )
        conn.commit()
            
        self.ungrade_db()
        
        lock_db.release()
        
        
        
    def open_insert_session(self):
        global lock_db
        lock_db.acquire()
        
        if self._insert_session :
            lock_db.release()
            raise Exception("Error: database.open_insert_session session already opened !")
        self._insert_session = True
        
        self._tracks = {}
        self._albums = {}
        self._artists = {}
        self._genre = {}
        self._codec = {}
        self._dr = {}
        self._date = {}
        
        self._id_artist = self.query( "select max(Id) from Artist" ).pop()[0]
        self._id_artist = 0 if self._id_artist == None else self._id_artist + 1
        
        self._id_album = self.query( "select max(Id) from Album" ).pop()[0]
        self._id_album = 0 if self._id_album == None else self._id_album + 1
        
        self._id_track = self.query( "select max(Id) from track" ).pop()[0]
        self._id_track = 0 if self._id_track == None else self._id_track + 1
        
        self._id_genre = self.query( "select max(Id) from Genre" ).pop()[0]
        self._id_genre = 0 if self._id_genre == None else self._id_genre + 1
        
        self._id_codec = self.query( "select max(Id) from Codec" ).pop()[0]
        self._id_codec = 0 if self._id_codec == None else self._id_codec + 1
        
        self._id_dr = self.query( "select max(Id) from DR" ).pop()[0]
        self._id_dr = 0 if self._id_dr == None else self._id_dr + 1
        
        self._id_date = self.query( "select max(Id) from Date" ).pop()[0]
        self._id_date = 0 if self._id_date == None else self._id_date + 1        
        
        lock_db.release()
    
    
    def commit_insert_session(self):
        global lock_db
        lock_db.acquire()
        if self._insert_session == False :
            lock_db.release()
            raise Exception("Error: database.commit_insert_session the session has not been opened !")
        
        conn = sqlite3.connect( get_db_path() )
        c = conn.cursor()
        
        for k_dr in self._dr.keys() :
            c.execute( "insert into DR ( Id , DR ) values ( ? , ? ) " , ( k_dr , self._dr[k_dr] ) )
            
        for k_artist in self._artists.keys() :
            c.execute( "insert into Artist ( Id , Name ) values ( ? , ? ) " , ( k_artist , self._artists[k_artist] ) )
            
        for k_codec in self._codec.keys() :
            c.execute( "insert into Codec ( Id , Name ) values ( ? , ? ) " , ( k_codec , self._codec[k_codec] ) )
            
        for k_genre in self._genre.keys() :
            c.execute( "insert into Genre ( Id , Name ) values ( ? , ? ) " , ( k_genre , self._genre[k_genre] ) )         
            
        for k_date in self._date.keys() :
            c.execute( "insert into Date ( Id , Date ) values ( ? , ? ) " , ( k_date , self._date[k_date] ) )                
         
        for k_album in self._albums.keys() :
            c.execute( "insert into Album ( Id , sha1 , title ) values ( ? , ? , ? ) " , 
                       ( self._albums[k_album][0] , k_album , self._albums[k_album][1] ) )
            
            c.execute( "insert into DR_Album ( IdDr , IdAlbum ) values ( ? , ? ) " , 
                       ( self._albums[k_album][2] , self._albums[k_album][0] ) )
            
            
        for k_track in self._tracks.keys() :
            
            if self._tracks[k_track].get( "track_nr" , None ) == None :
                c.execute( "insert into Track ( Id , Title , rms , peak , duration , sha1 ) values ( ? , ? , ? , ? , ? , ? ) " , 
                           ( self._tracks[k_track]["id"] , self._tracks[k_track]["title"] , self._tracks[k_track]["rms"] ,
                             self._tracks[k_track]["peak"] , self._tracks[k_track]["duration"] ,
                             k_track ) )
            else :
                c.execute( "insert into Track ( Id , Title , rms , peak , duration , sha1 , track_nr ) values ( ? , ? , ? , ? , ? , ? , ? ) " , 
                           ( self._tracks[k_track]["id"] , self._tracks[k_track]["title"] , self._tracks[k_track]["rms"] ,
                             self._tracks[k_track]["peak"] , self._tracks[k_track]["duration"] ,
                             k_track , self._tracks[k_track]["track_nr"] ) )
            
            c.execute( "insert into DR_Track ( IdDr , IdTrack ) values ( ? , ? ) " ,
                       ( self._tracks[k_track]["dr_id"] , self._tracks[k_track]["id"] ) )
            
            c.execute( "insert into Codec_Track ( IdCodec , IdTrack ) values ( ? , ? ) " , 
                       ( self._tracks[k_track]["codec_id"] , self._tracks[k_track]["id"] ) )
            
            if self._tracks[k_track]["genre_id"] >= 0 :
                c.execute( "insert into Genre_Track ( IdGenre , IdTrack ) values ( ? , ? ) " , 
                           ( self._tracks[k_track]["genre_id"] , self._tracks[k_track]["id"] ) )
            
            if self._tracks[k_track]["date_id"] >= 0 :
                c.execute( "insert into Date_Track ( IdDate , IdTrack ) values ( ? , ? ) " , 
                           ( self._tracks[k_track]["date_id"] , self._tracks[k_track]["id"] ) )
                
            if self._tracks[k_track]["artist_id"] >= 0 :
                c.execute( "insert into Artist_Track ( IdArtist , IdTrack ) values ( ? , ? ) " , 
                           ( self._tracks[k_track]["artist_id"] , self._tracks[k_track]["id"] ) )
            
            if self._tracks[k_track]["album_id"] >= 0 :
                c.execute( "insert into Album_Track ( IdAlbum , IdTrack ) values ( ? , ? ) " , 
                           ( self._tracks[k_track]["album_id"] , self._tracks[k_track]["id"] ) ) 
        
        conn.commit()
        conn.close()
        
        self._insert_session = False
        lock_db.release()
    
    
    
    def insert_track( self , track_sha1 , title , 
                      dr , rms , peak , duration , 
                      codec , album_sha1=None , artist=None , 
                      genre=None , date = None , track_nr=None ):
        
        
        global lock_db
        lock_db.acquire()
        if self._insert_session == False :
            lock_db.release()
            raise Exception("Error: database.insert_track the insert session has not been opened !")
        
        
        q = "select Id from track where sha1 = ? " 
        rq = self.query( q , (track_sha1,) )
        
        if len( rq ) > 0 :
            lock_db.release()
            return rq.pop()[0]
        
        artist_id = -1
        if artist != None :
            q = "select Id from artist where name = ? " 
            rq = self.query( q , ( artist, ))
            if len( rq ) == 0 and not ( artist in self._artists.values() ) :
                artist_id = self.__insert_artist( artist )
            elif len( rq ) > 0 :
                artist_id = rq.pop()[0]
            else :
                artist_id = [k for (k, v) in self._artists.items() if v == artist][0]
        
            
        q = "select Id from codec where name = ? "
        rq = self.query( q , ( codec, ) )
        if len( rq ) == 0 and not ( codec in self._codec.values() ) :
            codec_id = self.__insert_codec( codec )
        elif len( rq ) > 0 :
            codec_id = rq.pop()[0]
        else :
            codec_id = [k for (k, v) in self._codec.items() if v == codec][0]            
        
         
        genre_id = -1   
        if genre != None : 
            q = "select Id from Genre where name = ? " 
            rq = self.query( q , (genre,) )
            if len( rq ) == 0 and not ( genre in self._genre.values() ) :
                genre_id = self.__insert_genre( genre )
            elif len( rq ) > 0 :
                genre_id = rq.pop()[0]
            else :
                genre_id = [k for (k, v) in self._genre.items() if v == genre][0] 
        
                
        date_id = -1   
        if date != None :
            date_nr = int(float( date )) 
            q = "select Id from Date where date = ? " 
            rq = self.query( q , ( date_nr, ) )
            if len( rq ) == 0 and not ( date_nr in self._date.values() ) :
                date_id = self.__insert_date( date_nr )
            elif len( rq ) > 0 :
                date_id = rq.pop()[0]
            else :
                date_id = [k for (k, v) in self._date.items() if v == date_nr ][0]                 
        
                
        q = "select Id from DR where DR = ? "  
        rq = self.query( q , (dr,) )
        if len( rq ) == 0 and not ( dr in self._dr.values() ) :
            dr_id = self.__insert_dr( dr )
        elif len( rq ) > 0 :
            dr_id = rq.pop()[0]
        else :
            dr_id = [k for (k, v) in self._dr.items() if v == dr][0]
        
        
        album_id = -1
        if album_sha1 != None :
            rq = self.query( "select Id from Album where sha1 = ? " , ( album_sha1, ) )
            if len( rq ) == 0 and not album_sha1 in [ k for k in self._albums.keys() ] :
                album_id = None
            elif len( rq ) > 0 :
                album_id = rq.pop()[0]
            else :
                album_id = [ self._albums[k][0] for k in self._albums.keys() if k == album_sha1 ][0]
   
            
        self._tracks[track_sha1] = { "id": self._id_track , "title": title , "dr_id": dr_id , 
                                    "peak": peak , "rms": rms , "duration": duration ,
                                    "codec_id": codec_id , "album_sha1": album_sha1 , "artist_id": artist_id , 
                                    "genre_id": genre_id , "date_id": date_id , "album_id": album_id , "track_nr": track_nr }
        
        self._id_track = self._id_track + 1
        
        lock_db.release()
        
        return self._id_track - 1
    
        
    def insert_album( self , album_sha1 , title , dr ):
        global lock_db
        lock_db.acquire()
        
        #print( album_sha1 )
        q = "select Id from Album where sha1 = ? "  
        rq = self.query( q , ( album_sha1, )  )
        
        if len( rq ) > 0 :
            lock_db.release()
            return rq.pop()[0]

        q = "select Id from DR where DR = %d " % dr 
        rq = self.query( q )
        if len( rq ) == 0 and not ( dr in self._dr.values() ) :
            dr_id = self.__insert_dr( dr )
        elif len( rq ) > 0 :
            dr_id = rq.pop()[0]
        else :
            dr_id = [k for (k, v) in self._dr.items() if v == dr][0] 
        
        self._albums[album_sha1] = [ self._id_album , title , dr_id ]
        self._id_album = self._id_album + 1
        
        lock_db.release()
        
        return self._id_album - 1
        
    def __insert_artist( self , name ):
        
        self._artists[self._id_artist] = name
        self._id_artist = self._id_artist + 1
                
        return self._id_artist - 1
        
    def __insert_codec( self , codec ):
        
        self._codec[self._id_codec] = codec
        self._id_codec = self._id_codec + 1
                
        return self._id_codec - 1
    
    def __insert_genre( self , genre ):
        
        self._genre[self._id_genre] = genre
        self._id_genre = self._id_genre + 1
                
        return self._id_genre - 1
    
    def __insert_dr( self , dr ):
        
        self._dr[self._id_dr] = dr
        self._id_dr = self._id_dr + 1
                
        return self._id_dr - 1   
    
    def __insert_date( self , date ):
        
        self._date[self._id_date] = date
        self._id_date = self._id_date + 1
                
        return self._id_date - 1       
        
        
    def query( self , query , t = () ):
        conn = sqlite3.connect( get_db_path() )
        c = conn.cursor()
        
        c.execute( query , t )
        res_l = c.fetchall()
        c.close()
        
        return res_l
 
             
    def dr14_db_main_structure_v1(self):
        db = """
        
            create table Db_Version (
                Version integer not null unique 
            ) ;
            
            insert into Db_Version ( Version ) values ( 1 ) ;
        
            create table Artist (
                Id integer primary key autoincrement ,
                Name varchar(60)
            ) ;   
            create index Artist_indx on Artist ( Name ) ;
                    
                    
            create table Track (
                Id integer primary key autoincrement ,
                Title varchar(60) ,
                track_nr integer ,
                rms float ,
                peak float ,
                duration float ,
                sha1 varchar(40) not null                 
            ) ;
            create index Track_indx on Track ( sha1 ) ;
            create index Track_title_indx on Track ( Title ) ;
            
            
            create table Album (
                Id integer primary key autoincrement ,
                sha1 varchar(40) not null ,
                Title varchar(100) 
            ) ;
            create index Album_indx on Album ( sha1 ) ;
            create index Album_title_indx on Track ( Title ) ;  
            
            
            create table DR (
                Id integer primary key autoincrement ,
                DR integer not null unique 
            ) ;
            
            create table Date (
               Id integer primary key autoincrement ,
               Date integer not null unique 
            ) ;
            
            create table Codec (
                Id integer primary key autoincrement ,
                Name varchar[15] 
            ) ;
            
            insert into Codec ( Name ) values ( "wav" ) ;
            insert into Codec ( Name ) values ( "mp3" ) ;
            insert into Codec ( Name ) values ( "flac" ) ;
            insert into Codec ( Name ) values ( "mp4" ) ;
            insert into Codec ( Name ) values ( "ogg" ) ;
            insert into Codec ( Name ) values ( "ac3" ) ;
            insert into Codec ( Name ) values ( "wma" ) ;
            insert into Codec ( Name ) values ( "ape" ) ;
                        
            create table Genre (
                Id integer primary key autoincrement ,
                Name varchar(40) 
            ) ;
            
            create table DR_Track (
                IdDr integer not null ,
                IdTrack integer not null unique ,
                primary key ( IdDr , IdTrack ),
                foreign key ( IdDr ) references DR ( Id ),
                foreign key ( IdTrack ) references Track ( Id )
            ) ;
            
            create table Codec_Track (
                IdCodec integer not null ,
                IdTrack integer not null unique ,
                primary key ( IdCodec , IdTrack ),
                foreign key ( IdCodec ) references Codec ( Id ),
                foreign key ( IdTrack ) references Track ( Id )
            ) ;            
            
            create table DR_Album (
                IdDr integer not null ,
                IdAlbum integer not null unique ,
                primary key ( IdDr , IdAlbum ),
                foreign key ( IdDr ) references DR ( Id ),
                foreign key ( IdAlbum ) references Album ( Id )
            ) ;
            
            create table Genre_Track (
                IdGenre integer not null ,
                IdTrack integer not null unique ,
                primary key ( IdGenre , IdTrack ) ,
                foreign key ( IdGenre ) references Genre ( Id ) ,
                foreign key ( IdTrack ) references Track ( Id )
            ) ;
            
            create table Date_Track (
                IdDate integer not null ,
                IdTrack integer not null unique ,
                primary key ( IdDate , IdTrack ) ,
                foreign key ( IdDate ) references Date ( Id ) ,
                foreign key ( IdTrack ) references Track ( Id )
            ) ;         
            
            create table Artist_Track (
                IdArtist integer not null ,
                IdTrack integer not null unique ,
                primary key ( IdArtist , IdTrack ) ,
                foreign key ( IdArtist ) references Artist ( Id ) ,
                foreign key ( IdTrack ) references Track ( Id )
            ) ;     
                        
            create table Album_Track (
                IdAlbum integer not null ,
                IdTrack integer not null ,
                primary key ( IdAlbum , IdTrack ) ,
                foreign key ( IdAlbum ) references Album ( Id ) ,
                foreign key ( IdTrack ) references Track ( Id )
            ) ;
            
        """
        
        return db
    
    def ungrade_db(self):
        None
    
    

class dr_database_singletone():
    __database_singletone = None
    
    def get(self):
        if dr_database_singletone.__database_singletone == None :
            dr_database_singletone.__database_singletone = dr_database()
            
        return dr_database_singletone.__database_singletone
    



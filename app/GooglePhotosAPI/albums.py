from init_photo_service import service
import pandas as pd

"""
list method
"""

response = service.albums().list(
    pageSize=50,
    excludeNonAppCreatedData=False
).execute()

lstAlbums = []
lstAlbums.extend(response['albums'])

while True:
    try:
        response = service.albums().list(
            pageSize=50,
            excludeNonAppCreatedData=False,
            pageToken=response['nextPageToken']
        ).execute()
        lstAlbums.extend(response['albums'])
    except KeyError:
        break

df_albums = pd.DataFrame(lstAlbums)
df_albums.to_excel("./app/db/albums.xlsx")
print(df_albums.info)


"""
get method
"""
# my_album_id = df_albums[df_albums['title']=='測試']['id'][0]
my_album_id = df_albums['id'][0]
response = service.albums().get(albumId=my_album_id).execute()
# print(response)


"""
create method
"""

event_suffix = "event2"

request_body = {
    'album': {'title': f'My Family Photos: {event_suffix}'}
}
response_album_family_photos = service.albums().create(body=request_body).execute()
# print(response_album_family_photos)

"""
addEnrichment (album description)
"""
request_body = {
    'newEnrichmentItem': {
        'textEnrichment': {
            'text': 'This is my faily album'
        }
    },
    'albumPosition': {
        'position': 'LAST_IN_ALBUM'
    }
}
response = service.albums().addEnrichment(
    albumId=response_album_family_photos.get('id'),
    body=request_body
).execute()
# print(response)


"""
addEnrichment (album location aka map)
"""
request_body = {
    'newEnrichmentItem': {
        'locationEnrichment': {
            'location': {
                'locationName': 'San Francisco, IL',
                'latlng': {
                    'latitude': 41.875270,
                    'longitude': -87.18797
                }
            }
        }
    },
    'albumPosition': {
        'position': 'LAST_IN_ALBUM'
    }
}
response = service.albums().addEnrichment(
    albumId=response_album_family_photos.get('id'),
    body=request_body
).execute()



"""
addEnrichment (album map route)
"""
request_body = {
    'newEnrichmentItem': {
        'mapEnrichment': {
            'origin': {
                'locationName': 'Chicago, IL',
                'latlng': {
                    'latitude': 41.875270,
                    'longitude': -87.18797
                }
            },
            'destination': {
                'locationName': 'San Francisco, CA',
                'latlng': {
                    'latitude': 37.775981,
                    'longitude': -122.419343
                }
            }
        }
    },
    'albumPosition': {
        'position': 'FIRST_IN_ALBUM'
        }
}

response = service.albums().addEnrichment(
    albumId=response_album_family_photos.get('id'),
    body=request_body
).execute()


"""
Share and unshare methods
"""
request_body = {
    'sharedAlbumOptions': {
        'isCollaborative': True,
        'isCommentable': True
    }
}
response = service.albums().share(
    albumId=response_album_family_photos['id'],
    body=request_body
).execute()

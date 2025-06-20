"""
Recursos y rutas para la API de videos
"""
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from models.video import VideoModel
from models import db


# Campos para serializar respuestas
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'views': fields.Integer,
    'likes': fields.Integer
}

# Parser para los argumentos en solicitudes PUT (crear video)
video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Nombre del video es requerido", required=True)
video_put_args.add_argument("views", type=int, help="Número de vistas del video", required=True)
video_put_args.add_argument("likes", type=int, help="Número de likes del video", required=True)

# Parser para los argumentos en solicitudes PATCH (actualizar video)
video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="Nombre del video")
video_update_args.add_argument("views", type=int, help="Número de vistas del video")
video_update_args.add_argument("likes", type=int, help="Número de likes del video")

def abort_if_video_doesnt_exist(video_id):
    """
    Verifica si un video existe, y si no, aborta la solicitud
    
    Args:
        video_id (int): ID del video a verificar
    """
    video = VideoModel.query.filter_by(id=video_id).first()
    if not video:
        abort(404, message=f"No se encontro un video con el ID {video_id}")
    return video

class Video(Resource):
    """
    Recurso para gestionar videos individuales
    """

    @marshal_with(resource_fields)
    def get(self, video_id):
        """
        Obtener un video por ID
        ---
        parameters:
          - name: video_id
            in: path
            type: integer
            required: true
            description: ID del video
        responses:
          200:
            description: Video encontrado
            schema:
              id: Video
              properties:
                id:
                  type: integer
                name:
                  type: string
                views:
                  type: integer
                likes:
                  type: integer
          404:
            description: Video no encontrado
        """
        video = abort_if_video_doesnt_exist(video_id)
        return video

    @marshal_with(resource_fields)
    def put(self, video_id):
        """
        Crear un nuevo video
        ---
        parameters:
          - name: video_id
            in: path
            type: integer
            required: true
            description: ID del video
          - name: body
            in: body
            required: true
            schema:
              id: VideoInput
              required:
                - name
                - views
                - likes
              properties:
                name:
                  type: string
                views:
                  type: integer
                likes:
                  type: integer
        responses:
          201:
            description: Video creado
            schema:
              $ref: '#/definitions/Video'
          409:
            description: Ya existe un video con ese ID
        """
        args = video_put_args.parse_args()
        if VideoModel.query.filter_by(id=video_id).first():
            abort(409, message=f"Ya existe un video con el ID {video_id}")
        video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
        db.session.add(video)
        db.session.commit()
        return video, 201

    @marshal_with(resource_fields)
    def patch(self, video_id):
        """
        Actualizar un video existente
        ---
        parameters:
          - name: video_id
            in: path
            type: integer
            required: true
            description: ID del video
          - name: body
            in: body
            required: true
            schema:
              id: VideoUpdate
              properties:
                name:
                  type: string
                views:
                  type: integer
                likes:
                  type: integer
        responses:
          200:
            description: Video actualizado
            schema:
              $ref: '#/definitions/Video'
          404:
            description: Video no encontrado
        """
        args = video_update_args.parse_args()
        video = abort_if_video_doesnt_exist(video_id)
        if args['name'] is not None:
            video.name = args['name']
        if args['views'] is not None:
            video.views = args['views']
        if args['likes'] is not None:
            video.likes = args['likes']
        db.session.add(video)
        db.session.commit()
        return video

    def delete(self, video_id):
        """
        Eliminar un video
        ---
        parameters:
          - name: video_id
            in: path
            type: integer
            required: true
            description: ID del video
        responses:
          204:
            description: Video eliminado
          404:
            description: Video no encontrado
        """
        video = abort_if_video_doesnt_exist(video_id)
        db.session.delete(video)
        db.session.commit()
        return '', 204

class VideoList(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return VideoModel.query.all()
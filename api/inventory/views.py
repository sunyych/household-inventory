from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import InventoryItem
from .serializers import InventoryItemSerializer
from .services import run_sql_command, json_to_sql
from .tasks import transcribe_and_process_task
from celery.result import AsyncResult
from rest_framework.decorators import api_view
from .models import InventoryItem
from .serializers import InventoryItemSerializer
import os

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
   
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def transcribe_and_process(self, request):
        audio_file = request.data.get('file')
        if audio_file:
            shared_directory = '/shared/'
            if not os.path.exists(shared_directory):
                os.makedirs(shared_directory)

            file_path = os.path.join(shared_directory, audio_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            # Send the task to Celery
            task = transcribe_and_process_task.delay(file_path)
            return Response({"task_id": task.id})

        return Response({"error": "No file provided"}, status=400)
    
    @action(detail=False, methods=['get'], url_path='task_status')
    def task_status(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({"error": "Task ID not provided"}, status=400)
        
        result = AsyncResult(task_id)
        if result.state == 'SUCCESS':
            if 'instructions' in result.result:
                cmd = json_to_sql(result.result['instructions'])

                if len(cmd) > 0:
                    run_sql_command(cmd)

            return Response({"status": result.state, "result": result.result})
        elif result.state == 'FAILURE':
            return Response({"status": result.state, "error": str(result.result)})
        else:
            return Response({"status": result.state})
        
        
@api_view(['GET'])
def inventory_api_view(request):
    inventory_items = InventoryItem.objects.all()
    serializer = InventoryItemSerializer(inventory_items, many=True)
    return Response(serializer.data)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, F, Avg
from django.utils.timezone import make_aware, now
from datetime import datetime, timedelta
from collections import Counter
from .models import AlcoholRecord
from .serializers import AlcoholRecordSerializer

# 음주 기록을 생성하고 조회하는 API
class AlcoholRecordListCreateView(generics.ListCreateAPIView):
    queryset = AlcoholRecord.objects.all()
    serializer_class = AlcoholRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):  
            serializer = self.get_serializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Save all instances provided in the request
        serializer.save(user=self.request.user)

# 특정 날짜의 음주 기록을 조회, 업데이트, 삭제하는 API
class AlcoholRecordDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        # date_str을 사용하여 특정 날짜의 음주 기록을 조회
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        record = AlcoholRecord.objects.filter(user=request.user, date=date).first()
        
        if not record:
            return Response({'error': 'Record not found for the given date.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AlcoholRecordSerializer(record)
        return Response(serializer.data)

    def put(self, request, date_str):
        # date_str을 사용하여 특정 날짜의 음주 기록을 업데이트
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        record = AlcoholRecord.objects.filter(user=request.user, date=date).first()
        
        if not record:
            return Response({'error': 'Record not found for the given date.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AlcoholRecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, date_str):
        # date_str을 사용하여 특정 날짜의 음주 기록을 삭제
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        record = AlcoholRecord.objects.filter(user=request.user, date=date).first()
        
        if not record:
            return Response({'error': 'Record not found for the given date.'}, status=status.HTTP_404_NOT_FOUND)

        record.delete()
        return Response({'message': 'Record deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# 날짜별로 음주 측정량을 계산해주는 API
class MonthlyAlcoholConsumption(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year, month):
        start_date = make_aware(datetime(year, month, 1))
        end_date = make_aware(datetime(year, month + 1, 1)) if month < 12 else make_aware(datetime(year + 1, 1, 1))

        records = AlcoholRecord.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).annotate(
            total_alcohol_intake=F('servings') * F('alcohol_type__alcohol_content_per_serving')
        ).values('date').annotate(
            total_consumption=Sum('total_alcohol_intake')
        )

        response_data = {
            "year": year,
            "month": month,
            "data": list(records)
        }
        return Response(response_data)

# 사용자의 음주 패턴을 분석해주는 API
class AlcoholAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()
        first_day_of_month = today.replace(day=1)

        monthly_analysis = self.analyze_monthly_drinking(user, first_day_of_month, today)
        six_months_analysis = self.analyze_six_months_drinking(user, today)

        response_data = {
            "monthly_analysis": monthly_analysis,
            "six_months_analysis": six_months_analysis
        }

        return Response(response_data)

    def analyze_monthly_drinking(self, user, start_date, end_date):
        monthly_records = AlcoholRecord.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        )

        monthly_drink_count = monthly_records.count()
        drink_type_counts = monthly_records.values('alcohol_type__name').annotate(
            total_servings=Sum('servings')
        )

        avg_drinking_duration = monthly_records.aggregate(avg_duration=Avg('drinking_duration'))
        avg_weather = Counter(monthly_records.values_list('weather', flat=True))
        avg_mood = Counter(monthly_records.values_list('mood', flat=True))

        most_drunk_this_month = max(drink_type_counts, key=lambda x: x['total_servings'])['alcohol_type__name']

        return {
            "drink_count": monthly_drink_count,
            "drink_types": list(drink_type_counts),
            "avg_drinking_duration": avg_drinking_duration['avg_duration'],
            "avg_weather": avg_weather.most_common(1)[0][0] if avg_weather else None,
            "avg_mood": avg_mood.most_common(1)[0][0] if avg_mood else None,
            "most_drunk_this_month": most_drunk_this_month,
        }

    def analyze_six_months_drinking(self, user, end_date):
        six_months_ago = end_date - timedelta(days=180)
        six_month_records = AlcoholRecord.objects.filter(
            user=user,
            date__gte=six_months_ago,
            date__lte=end_date
        ).values('alcohol_type__name').annotate(
            total_servings=Sum('servings')
        )

        most_drunk_six_months = max(six_month_records, key=lambda x: x['total_servings'])['alcohol_type__name']

        return {
            "most_drunk_six_months": most_drunk_six_months
        }

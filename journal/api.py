from rest_framework import serializers, generics
from journal.models import Journal, Entry, Streak


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('created_at', 'txt')
        ordering = ['-created_at']


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = ('date_start', 'date_end', 'length')


class JournalSerializer(serializers.HyperlinkedModelSerializer):
    entries = EntrySerializer(many=True, read_only=True, source='entry_set')
    current_streak = StreakSerializer(read_only=True)
    longest_streak = StreakSerializer(read_only=True)
    phone = serializers.CharField(source='get_phone')

    class Meta:
        model = Journal
        fields = ('hashid', 'phone', 'created_at', 'last_updated', 'entries', 'longest_streak', 'current_streak')


class JournalViewSet(generics.RetrieveAPIView):
    lookup_field = 'hashid'
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer

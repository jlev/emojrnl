from rest_framework import serializers, generics
from journal.models import Journal, Entry


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('created_at', 'txt')


class JournalSerializer(serializers.HyperlinkedModelSerializer):
    entries = EntrySerializer(many=True, read_only=True, source='entry_set')

    class Meta:
        model = Journal
        fields = ('hashid', 'created_at', 'last_updated', 'entries')


class JournalViewSet(generics.RetrieveAPIView):
    lookup_field = 'hashid'
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer

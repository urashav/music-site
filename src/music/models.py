from django.db import models
from django.utils.text import slugify
from .services.ms2time import ms2time


class Playlist(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('in_process', 'В обработке...'),
        ('done', 'Готов'),
        ('error', 'Ошибка'),
        ('ready', 'Ожидает'),
    )

    full_url = models.CharField('Полный URL', null=False, blank=False, unique=True, max_length=255)
    original_id = models.BigIntegerField('Оригинальный ID', null=True, blank=True, unique=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='new')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Плейлист"
        verbose_name_plural = "Плейлисты"

    def __str__(self):
        return str(self.pk)


class Track(models.Model):
    """
    original_id Оригинальный id трека в сервисе
    permalink_url Прямая ссылка на источник
    stream_url  Конечный URL для воспроизведения композиции
    artwork_img_url Изображение композиции
    waveform_img_url Визуализация дорожки
    """
    slug = models.SlugField(allow_unicode=True, unique=True, max_length=255)
    original_id = models.BigIntegerField('Оригинальный ID', null=True, unique=True)
    title = models.CharField('Название', max_length=255, null=False)
    permalink_url = models.CharField('Ссылка', max_length=255, null=True)
    stream_url = models.CharField(max_length=255, null=True)
    artwork_img_url = models.CharField(max_length=255, null=True)
    waveform_img_url = models.CharField(max_length=255, null=True)
    duration = models.BigIntegerField(null=False, default=0)
    original_content_size = models.BigIntegerField(null=False, default=0)
    genre = models.CharField('Жанр', max_length=255, null=True)
    bpm = models.IntegerField(null=True, default=321)
    release_year = models.IntegerField(null=True)
    release_month = models.IntegerField(null=True)
    release_day = models.IntegerField(null=True)
    original_format = models.CharField('Формат', max_length=10, null=False, default="mp3")
    counter = models.BigIntegerField('Счетчик', null=False, default=0, blank=True)
    download_counter = models.BigIntegerField('Загрузили', null=False, default=0, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)
    playlist_id = models.ForeignKey(Playlist, on_delete=models.CASCADE, verbose_name='ID Плейлиста')

    def get_absolute_url(self):
        return f'/{self.slug}'

    def get_duration(self):
        duration = ms2time(self.duration)
        return duration

    def get_artist(self):
        title = self.title
        data = title.split("-")
        if len(data) < 2:
            return ""
        return data[0].strip()

    def get_song(self):
        title = self.title
        data = title.split("-")
        if len(data) < 2:
            return data[0].strip()
        if len(data) > 2:
            str = data[1:]
            return ' '.join(str)
        return data[1].strip()

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if is_new:
            self.slug = slugify(self.title, allow_unicode=True)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Трэк"
        verbose_name_plural = "Треки"

    def __str__(self):
        return self.title


class Keywords(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('in_process', 'В обработке...'),
        ('done', 'Готов'),
        ('error', 'Ошибка'),
    )

    keyword = models.CharField(verbose_name='Ключевое слово', max_length=255, null=False, blank=False)
    offset = models.IntegerField(verbose_name='Пропуск записей', null=False, default=0, blank=True)
    limit = models.IntegerField(verbose_name='Лимит записей', null=False, default=10, blank=True)
    total_results = models.IntegerField(verbose_name='Всего записей', null=False, default=0, blank=True, )
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Ключевые слова"
        verbose_name_plural = "Ключевые слова"

    def __str__(self):
        return self.keyword

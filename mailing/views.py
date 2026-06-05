from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.urls import reverse_lazy
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.views import View
from django.utils import timezone
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from mailing.forms import (
    RecipientForm,
    MessageForm,
    MailingForm,
)
from mailing.models import (
    Recipient,
    Message,
    Mailing,
    Attempt,
)
from mailing.services import send_mailing

MAILING_DASHBOARD_CACHE_TIMEOUT = 60 * 5


def get_mailing_dashboard_cache_key(user):
    if (
        user_can_view_all_recipients(user)
        or user_can_view_all_mailings(user)
    ):
        return 'mailing_dashboard_manager'

    return f'mailing_dashboard_user_{user.pk}'


def clear_mailing_dashboard_cache():
    try:
        cache.delete_pattern('mailing_dashboard_*')
    except AttributeError:
        cache.clear()


def user_can_view_all_recipients(user):
    return user.has_perm('mailing.can_view_all_recipients')


def user_can_view_all_mailings(user):
    return user.has_perm('mailing.can_view_all_mailings')


def user_can_disable_mailing(user):
    return user.has_perm('mailing.can_disable_mailing')


class MailingHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()

        if user_can_view_all_recipients(self.request.user):
            recipients_queryset = Recipient.objects.all()
        else:
            recipients_queryset = Recipient.objects.filter(
                owner=self.request.user
            )

        if user_can_view_all_mailings(self.request.user):
            mailings_queryset = Mailing.objects.all()
            attempts_queryset = Attempt.objects.all()
        else:
            mailings_queryset = Mailing.objects.filter(
                owner=self.request.user
            )
            attempts_queryset = Attempt.objects.filter(
                mailing__owner=self.request.user
            )

        context['recipients'] = recipients_queryset.order_by('-id')[:5]

        context['messages'] = Message.objects.filter(
            owner=self.request.user
        ).order_by('-id')[:5]

        context['mailings'] = mailings_queryset.order_by('-id')[:5]

        cache_key = get_mailing_dashboard_cache_key(
            self.request.user
        )
        cached_statistics = cache.get(cache_key)

        if cached_statistics is None:
            cached_statistics = {
                'total_mailings': mailings_queryset.count(),
                'active_mailings': mailings_queryset.filter(
                    start_time__lte=now,
                    end_time__gte=now
                ).count(),
                'finished_mailings': mailings_queryset.filter(
                    end_time__lt=now
                ).count(),
                'created_mailings': mailings_queryset.filter(
                    start_time__gt=now
                ).count(),
                'total_recipients': recipients_queryset.count(),
                'total_attempts': attempts_queryset.count(),
                'successful_attempts': attempts_queryset.filter(
                    status=Attempt.STATUS_SUCCESS
                ).count(),
                'failed_attempts': attempts_queryset.filter(
                    status=Attempt.STATUS_FAILED
                ).count(),
            }

            cache.set(
                cache_key,
                cached_statistics,
                MAILING_DASHBOARD_CACHE_TIMEOUT
            )

        context.update(cached_statistics)

        return context


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'

    def get_queryset(self):
        if user_can_view_all_recipients(self.request.user):
            queryset = Recipient.objects.all()
        else:
            queryset = Recipient.objects.filter(
                owner=self.request.user
            )

        search_query = self.request.GET.get('q')

        if search_query:
            queryset = queryset.filter(
                email__icontains=search_query
            )

        return queryset


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = 'mailing/recipient_detail.html'

    def get_queryset(self):
        if user_can_view_all_recipients(self.request.user):
            return Recipient.objects.all()

        return Recipient.objects.filter(
            owner=self.request.user
        )


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        recipient = form.save(commit=False)
        recipient.owner = self.request.user
        recipient.save()

        clear_mailing_dashboard_cache()

        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        clear_mailing_dashboard_cache()

        return super().form_valid(form)

    def get_queryset(self):
        return Recipient.objects.filter(
            owner=self.request.user
        )


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    def form_valid(self, form):
        clear_mailing_dashboard_cache()

        return super().form_valid(form)
    model = Recipient
    template_name = 'mailing/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_queryset(self):
        return Recipient.objects.filter(
            owner=self.request.user
        )


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'

    def get_queryset(self):
        return Message.objects.filter(
            owner=self.request.user
        )


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'

    def get_queryset(self):
        return Message.objects.filter(
            owner=self.request.user
        )


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()

        clear_mailing_dashboard_cache()

        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    def form_valid(self, form):
        clear_mailing_dashboard_cache()

        return super().form_valid(form)
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(
            owner=self.request.user
        )


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    def form_valid(self, form):
        clear_mailing_dashboard_cache()

        return super().form_valid(form)
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(
            owner=self.request.user
        )


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self):
        if user_can_view_all_mailings(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(
            owner=self.request.user
        )


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'

    def get_queryset(self):
        if user_can_view_all_mailings(self.request.user):
            return Mailing.objects.all()

        return Mailing.objects.filter(
            owner=self.request.user
        )

    def get_object(self, queryset=None):
        mailing = super().get_object(queryset)

        mailing.update_status()

        return mailing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['current_time'] = timezone.now()
        context['recipients_count'] = self.object.recipients.count()
        context['attempts'] = self.object.attempts.all().order_by(
            '-attempt_time'
        )
        context['attempts_count'] = context['attempts'].count()

        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        mailing = form.save(commit=False)

        mailing.owner = self.request.user

        mailing.save()

        form.save_m2m()

        clear_mailing_dashboard_cache()

        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(
            owner=self.request.user
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        clear_mailing_dashboard_cache()

        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    def form_valid(self, form):
        clear_mailing_dashboard_cache()

        return super().form_valid(form)
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(
            owner=self.request.user
        )


class MailingSendView(LoginRequiredMixin, View):

    def post(self, request, pk):
        if user_can_view_all_mailings(request.user):
            mailing = get_object_or_404(
                Mailing,
                pk=pk
            )
        else:
            mailing = get_object_or_404(
                Mailing,
                pk=pk,
                owner=request.user
            )

        try:
            attempts = send_mailing(mailing)
            clear_mailing_dashboard_cache()

            messages.success(
                request,
                f'Рассылка запущена. Создано попыток отправки: {len(attempts)}.'
            )

        except ValueError as error:
            messages.error(
                request,
                str(error)
            )

        return redirect(
            'mailing:mailing_detail',
            pk=mailing.pk
        )


class MailingDisableView(LoginRequiredMixin, View):

    def post(self, request, pk):
        if not user_can_disable_mailing(request.user):
            messages.error(
                request,
                'У вас нет прав для отключения рассылки.'
            )

            return redirect(
                'mailing:mailing_detail',
                pk=pk
            )

        mailing = get_object_or_404(
            Mailing,
            pk=pk
        )

        now = timezone.now()

        if mailing.start_time > now:
            mailing.start_time = now

        mailing.end_time = now
        mailing.status = Mailing.STATUS_FINISHED
        mailing.save(
            update_fields=[
                'start_time',
                'end_time',
                'status',
            ]
        )

        clear_mailing_dashboard_cache()

        messages.success(
            request,
            'Рассылка отключена.'
        )

        return redirect(
            'mailing:mailing_detail',
            pk=mailing.pk
        )

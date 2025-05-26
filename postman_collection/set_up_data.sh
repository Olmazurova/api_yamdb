case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

cd ../api_yamdb/
$python manage.py migrate
$python manage.py flush --no-input
echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
    u, _ = User.objects.get_or_create(username='superuser'); u.is_superuser = True; u.is_staff = True; u.email = 'superuser@admin.ru'; u.set_password('5eCretPaSsw0rD'); u.save(); \
    u, _ = User.objects.get_or_create(username='admin-user'); u.is_superuser = False; u.is_staff = False; u.role = 'admin'; u.email = 'admin-user@admin.ru'; u.set_password('5eCretPaSsw0rD'); u.save(); \
    u, _ = User.objects.get_or_create(username='moderator'); u.is_superuser = False; u.is_staff = False; u.role = 'moderator'; u.email = 'moderator@admin.ru'; u.set_password('5eCretPaSsw0rD'); u.save();" | $python manage.py shell
echo "Setup done."
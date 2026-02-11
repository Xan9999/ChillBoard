import os
import sys
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ChillBoard.settings")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()
from PIL import Image
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from boards.models import ImagePost
from django.core.files import File


current_user = None


def show_main_menu():
    print("\n===== ChillBoard - Tekstovni vmesnik =====")
    if current_user:
        print(f"  Prijavljen kot: {current_user.username}")
    else:
        print("  Nisi prijavljen")
    print()
    print("1. Prijava")
    print("2. Naloži sliko")
    print("3. Izbriši sliko")
    print("4. Poglej vse slike uporabnika")
    print("5. Poglej sliko po ID-ju")
    print("6. Odjava")
    print("0. Izhod")
    print("==========================================")
    return input("Izberi možnost: ").strip()


def login_action():
    global current_user
    if current_user:
        print(f"Že si prijavljen kot {current_user.username}. Najprej se odjavi.")
        return

    username = input("Uporabniško ime: ").strip()
    password = input("Geslo: ").strip()

    user = authenticate(username=username, password=password)
    if user is not None:
        current_user = user
        print(f"Uspešna prijava! Dobrodošel, {user.username}.")
    else:
        print("Napačno uporabniško ime ali geslo.")


def upload_image():
    global current_user
    if not current_user:
        print("Najprej se prijavi.")
        return

    file_path = input("Pot do slike: ").strip()
    if not os.path.isfile(file_path):
        print("Datoteka ne obstaja.")
        return

    caption = input("Opis (opcijsko): ").strip()
    pos_x = input("Pozicija X (privzeto 100): ").strip()
    pos_y = input("Pozicija Y (privzeto 100): ").strip()
    width = input("Širina (privzeto 200): ").strip()
    height = input("Višina (privzeto 200): ").strip()

    try:
        pos_x = int(pos_x) if pos_x else 100
        pos_y = int(pos_y) if pos_y else 100
        width = int(width) if width else 200
        height = int(height) if height else 200
    except ValueError:
        print("Neveljavne številke.")
        return

    with open(file_path, "rb") as f:
        django_file = File(f, name=os.path.basename(file_path))
        post = ImagePost(
            user=current_user,
            caption=caption,
            pos_x=pos_x,
            pos_y=pos_y,
            width=width,
            height=height,
        )
        post.image.save(os.path.basename(file_path), django_file, save=True)

    print(f"Slika naložena! (ID: {post.id})")


def delete_image():
    global current_user
    if not current_user:
        print("Najprej se prijavi.")
        return

    images = ImagePost.objects.filter(user=current_user).order_by("-created_at")
    if not images.exists():
        print("Nimaš nobene slike.")
        return

    print("\nTvoje slike:")
    for img in images:
        print(f"  ID: {img.id} | Opis: {img.caption or '(brez)'} | Datum: {img.created_at.strftime('%Y-%m-%d %H:%M')}")

    image_id = input("Vnesi ID slike za brisanje: ").strip()
    try:
        image_id = int(image_id)
    except ValueError:
        print("Neveljaven ID.")
        return

    try:
        image = ImagePost.objects.get(id=image_id, user=current_user)
    except ImagePost.DoesNotExist:
        print("Slika ne obstaja ali ni tvoja.")
        return

    confirm = input(f"Ali res želiš izbrisati sliko '{image.caption or image.id}'? (da/ne): ").strip().lower()
    if confirm == "da":
        image.image.delete(save=False)
        image.delete()
        print("Slika izbrisana.")
    else:
        print("Brisanje preklicano.")


def list_user_images():
    username = input("Uporabniško ime (pusti prazno za svoje): ").strip()

    if not username:
        if not current_user:
            print("Najprej se prijavi ali vnesi uporabniško ime.")
            return
        user = current_user
    else:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print("Uporabnik ne obstaja.")
            return

    images = ImagePost.objects.filter(user=user).order_by("-created_at")
    if not images.exists():
        print(f"Uporabnik '{user.username}' nima nobene slike.")
        return

    print(f"\nSlike uporabnika '{user.username}':")
    print(f"{'ID':<6} {'Opis':<30} {'Pozicija':<15} {'Velikost':<15} {'Datum'}")
    print("-" * 85)
    for img in images:
        print(
            f"{img.id:<6} "
            f"{(img.caption or '(brez)'):<30} "
            f"{img.pos_x},{img.pos_y:<13} "
            f"{img.width}x{img.height:<13} "
            f"{img.created_at.strftime('%Y-%m-%d %H:%M')}"
        )


def view_image_by_id():
    image_id = input("Vnesi ID slike: ").strip()
    try:
        image_id = int(image_id)
    except ValueError:
        print("Neveljaven ID.")
        return
    
    image = ImagePost.objects.filter(id=image_id).first()  # Preveri, ali slika obstaja
    if not image:
        print("Slika ne obstaja.")
        return
    else:
        img = Image.open(image.image)
        img.show()
    
def logout_action():
    global current_user
    if not current_user:
        print("Nisi prijavljen.")
        return
    print(f"Odjava uporabnika {current_user.username}.")
    current_user = None


if __name__ == "__main__":
    while True:
        choice = show_main_menu()
        if choice == "1":
            login_action()
        elif choice == "2":
            upload_image()
        elif choice == "3":
            delete_image()
        elif choice == "4":
            list_user_images()
        elif choice == "5":
            view_image_by_id()
        elif choice == "6":
            logout_action
        elif choice == "0":
            print("Nasvidenje!")
            break
        else:
            print("Neveljavna izbira.")
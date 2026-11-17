"""
rpg_battle_oop.py
=================
Turn-Based RPG Battle (Hero vs Boss Monster) berbasis CLI.
Tugas Pemrograman Berorientasi Objek (PBO) - menerapkan seluruh pilar OOP:
  1. Abstraction      -> class Karakter(ABC) + @abstractmethod
  2. Inheritance      -> Warrior, Mage, Monster mewarisi Karakter
  3. Polymorphism     -> override serang() & gunakan_skill() di tiap subclass
  4. Encapsulation    -> atribut private (__hp, __max_hp, __mana) + @property/@setter
  5. Constructor + Validasi (ValueError) + dunder method (__str__, __gt__)
  6. @classmethod     -> penghitung objek & factory method spawn_boss()
  7. @staticmethod    -> utilitas kalkulasi (critical hit & damage dasar)

Cara menjalankan:  python rpg_battle_oop.py   (Python 3.8+)
"""

import random
from abc import ABC, abstractmethod


# =============================================================================
# ABSTRACTION: Superclass abstrak. Tidak bisa diinstansiasi langsung.
# =============================================================================
class Karakter(ABC):
    """Kerangka dasar semua karakter di dalam game."""

    # --- Atribut KELAS (dipakai oleh @classmethod) ---
    __total_karakter = 0          # private class attribute: total semua objek
    __jumlah_per_kelas = {}       # private class attribute: hitungan per subclass

    # Batas validasi (konstanta kelas)
    MIN_HP, MAX_HP = 50, 500
    MAX_MANA_LIMIT = 200
    MAX_NAMA = 20
    PELUANG_CRIT = 0.10           # akan di-override oleh subclass
    BIAYA_SKILL = 20              # akan di-override oleh subclass

    # -------------------------------------------------------------------------
    # CONSTRUCTOR dengan VALIDASI: input salah -> raise ValueError
    # -------------------------------------------------------------------------
    def __init__(self, nama, max_hp, max_mana, kekuatan):
        if not isinstance(nama, str) or not nama.strip():
            raise ValueError("Nama tidak boleh kosong.")
        if len(nama.strip()) > self.MAX_NAMA:
            raise ValueError(f"Nama maksimal {self.MAX_NAMA} karakter.")
        if not isinstance(max_hp, int) or isinstance(max_hp, bool) \
                or not (self.MIN_HP <= max_hp <= self.MAX_HP):
            raise ValueError(f"HP harus bilangan bulat {self.MIN_HP}-{self.MAX_HP}.")
        if not isinstance(max_mana, int) or isinstance(max_mana, bool) \
                or not (0 <= max_mana <= self.MAX_MANA_LIMIT):
            raise ValueError(f"Mana harus bilangan bulat 0-{self.MAX_MANA_LIMIT}.")
        if not isinstance(kekuatan, int) or isinstance(kekuatan, bool) \
                or not (1 <= kekuatan <= 50):
            raise ValueError("Kekuatan harus bilangan bulat 1-50.")

        # ENCAPSULATION: atribut private (name mangling -> _Karakter__hp, dst.)
        self.nama = nama.strip()
        self.kekuatan = kekuatan
        self.__max_hp = max_hp
        self.__max_mana = max_mana
        self.__hp = max_hp
        self.__mana = max_mana

        # CLASSMETHOD dipanggil untuk mencatat objek baru
        self._catat_objek()

    # -------------------------------------------------------------------------
    # ENCAPSULATION: @property (getter) & @setter dengan pembatasan nilai
    # -------------------------------------------------------------------------
    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, nilai):
        if not isinstance(nilai, (int, float)) or isinstance(nilai, bool):
            raise ValueError("HP harus berupa angka.")
        # Nilai dijaga agar tidak < 0 dan tidak > max_hp
        self.__hp = max(0, min(int(nilai), self.__max_hp))

    @property
    def max_hp(self):          # read-only (tanpa setter)
        return self.__max_hp

    @property
    def mana(self):
        return self.__mana

    @mana.setter
    def mana(self, nilai):
        if not isinstance(nilai, (int, float)) or isinstance(nilai, bool):
            raise ValueError("Mana harus berupa angka.")
        # Nilai dijaga agar tidak < 0 dan tidak > max_mana
        self.__mana = max(0, min(int(nilai), self.__max_mana))

    @property
    def max_mana(self):        # read-only
        return self.__max_mana

    @property
    def hidup(self):           # property turunan (computed)
        return self.__hp > 0

    # -------------------------------------------------------------------------
    # CLASSMETHOD: pelacak total objek karakter
    # -------------------------------------------------------------------------
    @classmethod
    def _catat_objek(cls):
        # Akses lewat nama Karakter agar counter tidak "terpecah" ke subclass
        Karakter.__total_karakter += 1
        Karakter.__jumlah_per_kelas[cls.__name__] = \
            Karakter.__jumlah_per_kelas.get(cls.__name__, 0) + 1

    @classmethod
    def total_karakter(cls):
        return Karakter.__total_karakter

    @classmethod
    def rincian_karakter(cls):
        return dict(Karakter.__jumlah_per_kelas)

    # -------------------------------------------------------------------------
    # STATICMETHOD: utilitas kalkulasi (tidak butuh self/cls)
    # -------------------------------------------------------------------------
    @staticmethod
    def hitung_critical(peluang):
        """True jika serangan menjadi critical hit (peluang 0.0 - 1.0)."""
        return random.random() < peluang

    @staticmethod
    def hitung_damage_dasar(kekuatan, pengali=1.0):
        """Damage dasar = kekuatan * pengali, ditambah variasi acak +-20%."""
        variasi = random.uniform(0.8, 1.2)
        return max(1, int(kekuatan * pengali * variasi))

    # -------------------------------------------------------------------------
    # Method konkret yang dipakai bersama (reuse lewat INHERITANCE)
    # -------------------------------------------------------------------------
    def _hitung_serangan(self, pengali=1.0):
        """Mengembalikan (damage, apakah_critical)."""
        damage = Karakter.hitung_damage_dasar(self.kekuatan, pengali)
        crit = Karakter.hitung_critical(self.PELUANG_CRIT)
        if crit:
            damage = int(damage * 1.5)
        return damage, crit

    def terima_damage(self, damage):
        sebelum = self.hp
        self.hp = self.hp - damage          # lewat setter -> aman dari nilai negatif
        return sebelum - self.hp            # damage aktual yang diterima

    def pulihkan_mana(self, jumlah):
        self.mana = self.mana + jumlah

    # -------------------------------------------------------------------------
    # ABSTRACTION: method abstrak, WAJIB di-override oleh subclass
    # -------------------------------------------------------------------------
    @abstractmethod
    def serang(self, target):
        """Serangan biasa ke target."""

    @abstractmethod
    def gunakan_skill(self, target):
        """Skill spesial (memakai mana)."""

    # -------------------------------------------------------------------------
    # SPECIAL METHODS (dunder)
    # -------------------------------------------------------------------------
    def __str__(self):
        persen = self.hp / self.max_hp
        bar = "#" * int(persen * 10) + "." * (10 - int(persen * 10))
        return (f"[{self.__class__.__name__}] {self.nama:<14} "
                f"HP {self.hp:>3}/{self.max_hp:<3} [{bar}] "
                f"Mana {self.mana:>3}/{self.max_mana:<3} ATK {self.kekuatan}")

    def __gt__(self, other):
        # Perbandingan: karakter "lebih kuat" = HP lebih besar
        if not isinstance(other, Karakter):
            return NotImplemented
        return self.hp > other.hp


# =============================================================================
# INHERITANCE + POLYMORPHISM: Subclass dengan perilaku berbeda
# =============================================================================
class Warrior(Karakter):
    """Petarung jarak dekat: HP besar, skill murah, damage fisik."""
    PELUANG_CRIT = 0.20
    BIAYA_SKILL = 20

    def __init__(self, nama, max_hp=150, max_mana=50, kekuatan=18):
        super().__init__(nama, max_hp, max_mana, kekuatan)   # panggil constructor induk

    # OVERRIDE
    def serang(self, target):
        damage, crit = self._hitung_serangan()
        nyata = target.terima_damage(damage)
        tanda = " (CRITICAL!)" if crit else ""
        return f"{self.nama} menebas {target.nama} -> {nyata} damage{tanda}"

    # OVERRIDE
    def gunakan_skill(self, target):
        self.mana = self.mana - self.BIAYA_SKILL
        damage, crit = self._hitung_serangan(pengali=2.0)
        nyata = target.terima_damage(damage)
        tanda = " (CRITICAL!)" if crit else ""
        return (f"{self.nama} memakai 'Tebasan Berani'! "
                f"{target.nama} kena {nyata} damage{tanda}")


class Mage(Karakter):
    """Penyihir: HP kecil, mana besar, skill sangat kuat."""
    PELUANG_CRIT = 0.15
    BIAYA_SKILL = 30

    def __init__(self, nama, max_hp=100, max_mana=120, kekuatan=14):
        super().__init__(nama, max_hp, max_mana, kekuatan)

    # OVERRIDE
    def serang(self, target):
        damage, crit = self._hitung_serangan()
        nyata = target.terima_damage(damage)
        tanda = " (CRITICAL!)" if crit else ""
        return f"{self.nama} menembakkan sihir kecil ke {target.nama} -> {nyata} damage{tanda}"

    # OVERRIDE
    def gunakan_skill(self, target):
        self.mana = self.mana - self.BIAYA_SKILL
        damage, crit = self._hitung_serangan(pengali=3.0)
        nyata = target.terima_damage(damage)
        tanda = " (CRITICAL!)" if crit else ""
        return (f"{self.nama} merapal 'Bola Api'! "
                f"{target.nama} terbakar {nyata} damage{tanda}")


class Monster(Karakter):
    """Boss monster, dibuat lewat factory method spawn_boss()."""
    PELUANG_CRIT = 0.10
    BIAYA_SKILL = 25

    def __init__(self, nama, max_hp=300, max_mana=100, kekuatan=15):
        super().__init__(nama, max_hp, max_mana, kekuatan)

    # CLASSMETHOD sebagai FACTORY METHOD: membuat boss sesuai level
    @classmethod
    def spawn_boss(cls, level=1):
        if not isinstance(level, int) or isinstance(level, bool) or not (1 <= level <= 5):
            raise ValueError("Level boss harus bilangan bulat 1-5.")
        daftar_nama = {1: "Goblin King", 2: "Orc Warlord", 3: "Dark Troll",
                       4: "Vampire Lord", 5: "Ancient Dragon"}
        return cls(nama=daftar_nama[level],
                   max_hp=150 + level * 50,        # 200 .. 400
                   max_mana=60 + level * 20,
                   kekuatan=10 + level * 3)

    # OVERRIDE
    def serang(self, target):
        damage, crit = self._hitung_serangan()
        nyata = target.terima_damage(damage)
        tanda = " (CRITICAL!)" if crit else ""
        return f"{self.nama} mencakar {target.nama} -> {nyata} damage{tanda}"

    # OVERRIDE
    def gunakan_skill(self, target):
        self.mana = self.mana - self.BIAYA_SKILL
        damage, crit = self._hitung_serangan(pengali=1.8)
        nyata = target.terima_damage(damage)
        tanda = " (CRITICAL!)" if crit else ""
        return (f"{self.nama} menyemburkan 'Raungan Api'! "
                f"{target.nama} kena {nyata} damage{tanda}")


# =============================================================================
# Fungsi bantu input pemain (penanganan ValueError dengan try-except)
# =============================================================================
def baca_angka(prompt, minimum, maksimum):
    """Membaca bilangan bulat; ValueError ditangani oleh pemanggil."""
    teks = input(prompt).strip()
    angka = int(teks)                     # int('abc') -> ValueError
    if not (minimum <= angka <= maksimum):
        raise ValueError(f"Nilai harus antara {minimum} dan {maksimum}.")
    return angka


def buat_hero():
    """Meminta data hero sampai valid. Error dari __init__ ditangkap di sini."""
    while True:
        try:
            nama = input("Nama hero            : ")
            pilihan = input("Kelas [1] Warrior [2] Mage : ").strip()
            kelas = {"1": Warrior, "2": Mage}.get(pilihan)
            if kelas is None:
                raise ValueError("Pilihan kelas harus 1 atau 2.")
            hp_teks = input("HP awal (50-500, Enter = default): ").strip()
            if hp_teks == "":
                return kelas(nama)
            return kelas(nama, max_hp=int(hp_teks))   # validasi di constructor
        except ValueError as err:
            print(f"  [!] Input tidak valid: {err}\n      Silakan ulangi.\n")


def pilih_level_boss():
    while True:
        try:
            level = baca_angka("Level boss (1-5)     : ", 1, 5)
            return Monster.spawn_boss(level)          # factory method
        except ValueError as err:
            print(f"  [!] Input tidak valid: {err}\n")


# =============================================================================
# Alur permainan
# =============================================================================
def giliran_boss(boss, hero):
    """POLYMORPHISM: boss dipanggil lewat interface yang sama (serang/skill)."""
    if boss.mana >= boss.BIAYA_SKILL and random.random() < 0.4:
        return boss.gunakan_skill(hero)
    return boss.serang(hero)


def main():
    print("=" * 62)
    print("        TURN-BASED RPG BATTLE  -  Hero vs Boss Monster")
    print("=" * 62)

    # Bukti ABSTRACTION: kelas abstrak tidak boleh dibuat langsung
    try:
        Karakter("Test", 100, 50, 10)
    except TypeError:
        print("(Info) Karakter adalah kelas abstrak -> tidak bisa diinstansiasi.\n")

    hero = buat_hero()
    boss = pilih_level_boss()

    print("\n--- Peserta Pertarungan ---")
    print(hero)
    print(boss)
    print(f"Total objek karakter dibuat : {Karakter.total_karakter()} "
          f"{Karakter.rincian_karakter()}")
    print(f"Hero lebih kuat dari boss? (hero > boss) : {hero > boss}")

    ronde = 1
    while hero.hidup and boss.hidup:
        print(f"\n===== RONDE {ronde} =====")
        print(hero)
        print(boss)
        print("[1] Serang   [2] Skill   [3] Istirahat (+mana)")

        # --- Giliran pemain ---
        try:
            aksi = baca_angka("Pilih aksi: ", 1, 3)
        except ValueError as err:
            print(f"  [!] Pilihan tidak valid: {err} Coba lagi.")
            continue                                  # ronde tidak maju

        if aksi == 1:
            print(">>", hero.serang(boss))
        elif aksi == 2:
            if hero.mana < hero.BIAYA_SKILL:
                print(f"  [!] Mana kurang! Skill butuh {hero.BIAYA_SKILL} mana.")
                continue
            print(">>", hero.gunakan_skill(boss))
        else:
            hero.pulihkan_mana(25)
            print(f">> {hero.nama} beristirahat, mana +25.")

        # --- Giliran boss ---
        if boss.hidup:
            print(">>", giliran_boss(boss, hero))

        # Regenerasi mana kecil tiap ronde (dijaga oleh setter)
        hero.pulihkan_mana(5)
        boss.pulihkan_mana(5)
        ronde += 1

    print("\n" + "=" * 62)
    if hero.hidup:
        print(f"  VICTORY! {hero.nama} mengalahkan {boss.nama} dalam {ronde - 1} ronde.")
    else:
        print(f"  DEFEAT... {hero.nama} tumbang oleh {boss.nama}.")
    print("=" * 62)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPermainan dihentikan.")
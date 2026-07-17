# Correspondence System

**Sistema Jestaun Karta Tama no Sai ho Fluxu Aprovasaun no Monitorizasaun**

Sistema dijitál ba sirkulasaun dokumentu (paperless) iha **Gabinete Prezidente Autoridade RAEOA / ZEEMS-TL**. Dezenvolve ho Django Framework 5.x no MySQL.

## Funsaun Prinsipál

- **Karta Tama** — Rejistu, upload PDF, despaxu husi Prezidente
- **Karta Sai** — Drafting, workflow aprovasaun hierárkiku, aprova/rejeita
- **Monitorizasaun** — Deadline tracking, dashboard estatístika, notifikasaun automátiku
- **Autentikasaun** — Login seguru, perfil utilizadór, kontrolu asesu bazeia ba kargu (RBAC)

## Dokumentasaun

- [SRD — Dokumentu Spesifikasaun Rekizitu Sistema](docs/SRD.md)

## Teknolojia

| Komponente | Tecnologia |
|---|---|
| Framework | Django 5.x |
| Database | MySQL |
| Frontend | Bootstrap / Tailwind CSS (Mobile Responsive) |
| Seguransa | PBKDF2 + SHA256, RBAC, Secure Media Access |

## Instituisaun

Projetu ida ne'e dezenvolve husi estudante sira husi **Departamentu Informátika**, **Fakuldade Engenharia, Siénsia no Teknolojia (FEST)**, **Universidade Nacional Timor Lorosa'e (UNTL)**, hanesan parte husi projetu akadémiku atu dezenvolve sistema informasaun dijitál.
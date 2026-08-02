# ✅ Sanity Check – L3akCTF 2026

**Categoría:** Beginner  
**Dificultad:** Muy Fácil  
**Puntos:** 1  
**Flag:** `L3AK{w3LCom3_t0_L3AKCTF_2026_H4pPy_H@cK1nG!}`

---

## 📖 Descripción

El reto más básico del CTF. Solo requiere leer las reglas del torneo para encontrar la flag.

**Pista:** La flag está escondida a simple vista en las reglas.

---

## 🔍 Reconocimiento

1. Accedemos a la página de reglas del CTF:
   - URL: `https://ctf.l3ak.team/rules`

2. Al cargar la página, vemos una lista de normas del torneo.

---

## 💡 Solución

La flag aparece literalmente al final de las reglas:

```text
# Rules

- The flag format is L3AK{[ -~]+}
- No flag sharing or collaboration between teams.
- Players can only be a member of one team.
- There is no team size limit.
- Attacking the CTF infrastructure is prohibited, along with the use of any bruteforce/scanning tools like gobuster, sqlmap, etc.
- If you have an issue with a challenge, forget your account password, or otherwise need to contact an admin, please open a ticket in the Discord server
- AI assistance will be strictly prohibited in L3akCTF 2026. AI usage will result in immediate disqualification. Leave your agents and LLMs at home; this competition is for humans only.
- Organizers reserve the ultimate right to enforce rules not listed here at their own discretion.

L3AK{w3LCom3_t0_L3AKCTF_2026_H4pPy_H@cK1nG!}

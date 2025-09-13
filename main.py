from ivr.menus import select_language, run_ivr

def main():
    # 1) Seleciona idioma por voz (PT/EN)
    lang_data, code = select_language()
    # 2) Roda o IVR no idioma escolhido
    run_ivr(lang_data, code)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")

"""
Script de automação para mesclagem de PDFs de resumos.

Regras de negócio:
1. Prioriza o arquivo "1_TI TOTAL - Aula 26 - ISO 27002 - Resumo.pdf" na 1ª posição,
   mantendo todas as suas páginas originais.
2. Processa os demais PDFs em ordem alfabética natural, descartando a 1ª página (índice 0)
   de cada um e aproveitando da página 2 em diante.
3. Salva o resultado final consolidado como "TI_TOTAL_Compilado.pdf".
4. Trata arquivos de página única com segurança e exibe logs detalhados de execução.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import sys
from pypdf import PdfReader, PdfWriter

FIRST_FILE_NAME = "1_TI TOTAL - Aula 26 - ISO 27002 - Resumo.pdf"
DEFAULT_OUTPUT_NAME = "TI_TOTAL_Compilado.pdf"


def natural_sort_key(s: str):
    """
    Chave de ordenação natural que divide a string em blocos numéricos e de texto.
    Exemplo: 'Aula 2' vem antes de 'Aula 10'.
    """
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", s)]


def resolve_pdf_directory(input_dir: str | None = None) -> Path:
    """
    Detecta automaticamente o diretório de PDFs:
    - Se informado explicitamente via argumento, usa o diretório especificado.
    - Se existir a subpasta 'pdfs' com arquivos PDF, dá preferência a ela.
    - Caso contrário, usa o diretório atual de execução.
    """
    if input_dir:
        path = Path(input_dir)
        if not path.is_dir():
            raise FileNotFoundError(f"O diretório especificado não foi encontrado: {path}")
        return path

    cwd = Path.cwd()
    sub_pdfs = cwd / "pdfs"
    if sub_pdfs.is_dir():
        pdfs = list(sub_pdfs.glob("*.pdf"))
        if pdfs:
            return sub_pdfs

    return cwd


def get_ordered_pdf_list(pdf_dir: Path, output_filename: str) -> tuple[list[Path], Path | None]:
    """
    Retorna a lista ordenada de arquivos PDF para o merge:
    1. Arquivo prioritário '1_TI TOTAL - Aula 26 - ISO 27002 - Resumo.pdf' (se existir).
    2. Demais PDFs ordenados alfabética/naturalmente.
    Ignora qualquer arquivo de saída gerado anteriormente.
    """
    all_pdfs = [
        p for p in pdf_dir.iterdir()
        if p.is_file() and p.suffix.lower() == ".pdf" and p.name.lower() != output_filename.lower()
    ]

    priority_file: Path | None = None
    remaining_files: list[Path] = []

    for pdf in all_pdfs:
        if pdf.name.strip().lower() == FIRST_FILE_NAME.lower():
            priority_file = pdf
        else:
            remaining_files.append(pdf)

    # Ordenação natural dos demais arquivos
    remaining_files.sort(key=lambda p: natural_sort_key(p.name))

    ordered_list: list[Path] = []
    if priority_file:
        ordered_list.append(priority_file)
    ordered_list.extend(remaining_files)

    return ordered_list, priority_file


def merge_pdfs(
    input_dir: Path,
    output_filename: str = DEFAULT_OUTPUT_NAME,
    add_bookmarks: bool = True
) -> Path:
    """
    Executa o processo de mesclagem conforme as regras especificadas.
    """
    print("=" * 80)
    print("   PROCESSADOR E CONSOLIDADOR DE RESUMOS EM PDF")
    print("=" * 80)
    print(f"Diretório de trabalho: {input_dir.resolve()}")
    print(f"Arquivo consolidado de saída: {output_filename}\n")

    files_to_process, priority_file = get_ordered_pdf_list(input_dir, output_filename)

    if not files_to_process:
        print("[ERRO] Nenhum arquivo PDF encontrado para processar.")
        sys.exit(1)

    print(f"Total de PDFs localizados: {len(files_to_process)}")
    if priority_file:
        print(f"[OK] Arquivo prioritário identificado: '{priority_file.name}'")
    else:
        print(f"[AVISO] Arquivo prioritário '{FIRST_FILE_NAME}' não foi encontrado. Prosseguindo com ordenação natural.")

    print("\nIniciando consolidação...\n" + "-" * 80)
    print(f"{'#':<3} | {'Arquivo':<50} | {'Orig.':<6} | {'Mantidas':<8} | {'Observação'}")
    print("-" * 80)

    writer = PdfWriter()
    total_pages_consolidated = 0
    successful_files = 0

    for idx, pdf_path in enumerate(files_to_process, start=1):
        is_priority = (priority_file is not None and pdf_path == priority_file)
        
        try:
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)

            if total_pages == 0:
                print(f"{idx:<3} | {pdf_path.name[:48]:<50} | {0:<6} | {0:<8} | [AVISO] Arquivo vazio (0 páginas)")
                continue

            # Determina quais páginas manter
            if is_priority:
                # Mantém todas as páginas (índices 0 a N-1)
                pages_to_keep = list(range(total_pages))
                note = "Todas as páginas mantidas (Prioritário)"
            else:
                # Descarta a primeira página (índice 0), mantendo de 1 em diante
                if total_pages == 1:
                    pages_to_keep = []
                    note = "[AVISO] 1 pág descartada (0 mantidas)"
                else:
                    pages_to_keep = list(range(1, total_pages))
                    note = f"Págs 2-{total_pages} (1ª pág descartada)"

            # Adiciona marcador (bookmark/outline) no sumário do PDF consolidado
            if add_bookmarks and pages_to_keep:
                # Remove a extensão .pdf para o título no sumário
                clean_title = pdf_path.stem
                writer.add_outline_item(
                    title=f"{idx:02d}. {clean_title}",
                    page_number=total_pages_consolidated
                )

            # Adiciona as páginas ao escritor final
            for p_idx in pages_to_keep:
                writer.add_page(reader.pages[p_idx])

            pages_kept_count = len(pages_to_keep)
            total_pages_consolidated += pages_kept_count
            successful_files += 1

            print(f"{idx:<3} | {pdf_path.name[:48]:<50} | {total_pages:<6} | {pages_kept_count:<8} | {note}")

        except Exception as exc:
            print(f"{idx:<3} | {pdf_path.name[:48]:<50} | {'ERRO':<6} | {0:<8} | [FALHA] {exc}")

    print("-" * 80)

    if total_pages_consolidated == 0:
        print("[ERRO] Nenhuma página foi adicionada ao arquivo final. Abortando gravação.")
        sys.exit(1)

    # Gravação do arquivo consolidado no diretório dos PDFs
    output_path = input_dir / output_filename
    print(f"\nGravando arquivo consolidado em: {output_path} ...")
    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    # Se o diretório for uma subpasta (ex: 'pdfs'), também salva uma cópia na raiz do projeto para conveniência
    project_root = Path.cwd()
    root_copy_path = project_root / output_filename
    if input_dir.resolve() != project_root.resolve():
        try:
            shutil.copy2(output_path, root_copy_path)
            print(f"[OK] Cópia de fácil acesso gerada na raiz do projeto: {root_copy_path}")
        except Exception as copy_err:
            print(f"[AVISO] Não foi possível copiar para a raiz: {copy_err}")

    print("\n" + "=" * 80)
    print("                      CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print(f" • Arquivos processados com sucesso: {successful_files}/{len(files_to_process)}")
    print(f" • Total de páginas consolidadas:   {total_pages_consolidated} páginas")
    print(f" • Tamanho do arquivo gerado:        {file_size_mb:.2f} MB")
    print(f" • Local do arquivo gerado:         {output_path.resolve()}")
    print("=" * 80)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Consolida múltiplos PDFs em um único arquivo, com regras personalizadas de ordenação e descarte."
    )
    parser.add_argument(
        "-d", "--dir",
        dest="input_dir",
        default=None,
        help="Diretório onde estão os PDFs (padrão: detecta pasta 'pdfs' ou pasta atual)"
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_filename",
        default=DEFAULT_OUTPUT_NAME,
        help=f"Nome do arquivo final consolidado (padrão: {DEFAULT_OUTPUT_NAME})"
    )
    parser.add_argument(
        "--no-bookmarks",
        dest="no_bookmarks",
        action="store_true",
        help="Desativa a geração de marcadores (sumário/outline) no PDF final"
    )

    args = parser.parse_args()

    try:
        resolved_dir = resolve_pdf_directory(args.input_dir)
        merge_pdfs(
            input_dir=resolved_dir,
            output_filename=args.output_filename,
            add_bookmarks=not args.no_bookmarks
        )
    except Exception as e:
        print(f"\n[ERRO FATAL] Ocorreu um erro durante a execução: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


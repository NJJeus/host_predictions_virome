import os

# --- Configuration ---
INPUT_DIR = "DATA/TEST_VIRUS"
OUTPUT_BASE_DIR = "OUTPUTS_TEST"
ZOONOTIC_RUN_DIR = "zoonotic_rank"

# Automatically find all .fasta and .fa files in the input directory
SAMPLES, = glob_wildcards(os.path.join(INPUT_DIR, "{sample}.fasta"))
# If you have a mix of .fa and .fasta, we can collect both:
SAMPLES_FA, = glob_wildcards(os.path.join(INPUT_DIR, "{sample}.fa"))
ALL_SAMPLES = SAMPLES + SAMPLES_FA

rule all:
    input:
        expand(os.path.join(OUTPUT_BASE_DIR, "PREDICTIONS/{sample}.predictions.csv"), sample=ALL_SAMPLES)

rule install_zoontic_rank:
    output:
        directory("zoonotic_rank")
    shell:
        """
        git clone https://github.com/Nardus/zoonotic_rank.git
        """

rule run_prodigal:
    input:
        lambda wildcards: os.path.join(INPUT_DIR, wildcards.sample + (".fasta" if wildcards.sample in SAMPLES else ".fa"))
    output:
        gff = os.path.join(OUTPUT_BASE_DIR, "GFF/{sample}.gff")
    conda:
        "envs/prodigal.yaml"  # Path to a conda env file
    shell:
        """
        prodigal \
            -i {input} \
            -o {output.gff} \
            -p meta \
            -f gff
        """

rule process_gff:
    input:
        gff = os.path.join(OUTPUT_BASE_DIR, "GFF/{sample}.gff")
    output:
        csv = os.path.join(OUTPUT_BASE_DIR, "GFF/{sample}.csv")
    shell:
        "python process_prodigal.py {input.gff} {output.csv}"



rule zoonotic_ranking:
    input:
        tool = rules.install_zoontic_rank.output
        fasta = lambda wildcards: os.path.join(INPUT_DIR, wildcards.sample + (".fasta" if wildcards.sample in SAMPLES else ".fa")),
        csv = os.path.join(OUTPUT_BASE_DIR, "GFF/{sample}.csv")
    output:
        prediction = os.path.join(OUTPUT_BASE_DIR, "PREDICTIONS/{sample}.predictions.csv")
    conda:
        "envs/zoonotic_rank.yaml"
    params:
        run_dir = ZOONOTIC_RUN_DIR,
        out_dir= 'OUTPUTS_TEST/PREDICTIONS/{sample}'
    shell:
        """
        cd {params.run_dir} && \
        Rscript Scripts/PredictNovel.R fasta \
            ../{input.fasta} \
            ../{input.csv} \
            ../{params.out_dir}
        """

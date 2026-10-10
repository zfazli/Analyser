from parser.theia_parser import TheiaParser


datasets = [
    ("F:/dataset/theia_e5",
     "./process_result/theia-e5",
     "20"),

    # ("F:/dataset/theia_e3",
    #  "./process_result/theia-e3",
    #  "18"),



    # ("F:/dataset/trace_e5",
    #  "./process_result/trace-e5-all",
    #  "20")
]

for input_dir, output_dir, version in datasets:

    print("=" * 60)
    print(input_dir)
    print("=" * 60)
    parser = TheiaParser(

        input_dir=input_dir,

        output_dir=output_dir,

        version=version,

        chunk_size=1_000_000

    )

    # parser = FiveParser(

    #     input_dir=input_dir,

    #     output_dir=output_dir,

    #     version=version,

    #     chunk_size=1_000_000

    # )

    parser.parse()
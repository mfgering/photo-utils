from imagededup.methods import PHash

if __name__ == '__main__':
    phasher = PHash()

    # Generate encodings for all images in an image directory
    encodings = phasher.encode_images(image_dir='images-dedup')

    # Find duplicates using the generated encodings
    duplicates = phasher.find_duplicates(encoding_map=encodings)

    # plot duplicates obtained for a given file using the duplicates dictionary
    from imagededup.utils import plot_duplicates
    plot_duplicates(image_dir='images-dedup',
                    duplicate_map=duplicates,
                    filename='dog.jpg')

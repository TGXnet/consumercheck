from dataset_container import DatasetContainer

dsc = DatasetContainer()

dsc.read_datasets('/home/thomas/.config/ConsumerCheck.pkl')

nm = dsc.get_id_name_map()
print(nm)

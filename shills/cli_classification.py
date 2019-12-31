import metapy

fidx = metapy.index.make_forward_index('manually_tagged_backhanded.toml')
print(fidx.num_labels())

dset = metapy.classify.MulticlassDataset(fidx)
print(len(dset))
print(set([dset.label(instance) for instance in dset]))
view = metapy.classify.MulticlassDatasetView(dset)
print("{} vs {}".format(view[0].id, dset[0].id))
view.shuffle()
training = view[0:int(0.75*len(view))]
testing = view[int(0.75*len(view)):len(view)+1]
nb = metapy.classify.NaiveBayes(training)
print(nb.classify(testing[0].weights))
mtrx = nb.test(testing)
print(mtrx)


# mtrx.print_stats()
# mtrx = metapy.classify.cross_validate(lambda fold: metapy.classify.NaiveBayes(fold), view, 5)
# print(mtrx)
# mtrx.print_stats()

# review_fidx = metapy.index.make_forward_index('film_2.toml')
# print(review_fidx.num_labels())
# dset2 = metapy.classify.MulticlassDataset(review_fidx)
# view2 = metapy.classify.MulticlassDatasetView(dset2)
# testing2 = view2[0:len(view2)]
# print(testing2[0])
# print(nb.classify(testing2[0].weights))


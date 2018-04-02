import dcase_util
repo = dcase_util.utils.Example.feature_repository()
dcase_util.data.Stacker(recipe='mfcc=1,5,7').stack(repo).plot()
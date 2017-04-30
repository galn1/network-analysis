from operator import itemgetter
import learning.FeturesMatrix as features_matrix
import numpy as np
from learning import simple_machine_learning as ml
from graph_features import features as features


def buid_features_importance_dict(map_fetures):
    place = 0
    features_importance_dict = {}
    vertices_algo_dict = features.vertices_algo_dict
    features_list = []

    for key_feature in map_fetures.keys():
        features_list.append(vertices_algo_dict.keys()[vertices_algo_dict.values().index(key_feature)])


    for k, v in sorted(features.vertices_algo_dict.items(), key=itemgetter(1)):
        if k not in features_list:
            continue
        if k not in features.vertices_algo_feature_directed_length_dict:
            features_importance_dict[place] = k
            place += 1
        else:
            for i in range(features.vertices_algo_feature_directed_length_dict[k]):
                features_importance_dict[place] = k + '[' + str(i) + ']'
                place += 1

    # print features_importance_dict

    for k in features_list:
        print k
        if not features.vertices_algo_feature_directed_length_dict.has_key(k):
            place += 1
        else:
            print k
            place += features.vertices_algo_feature_directed_length_dict[k]
    print place


def machineLearning(gnx, map_fetures, number_of_learning_for_mean, classifications, ml_algos, tags_loader,
                result_path,edges=False):

    features_importance_dict = buid_features_importance_dict(map_fetures)

    if(edges):
        for classification in classifications:
            edges_to_tags = tags_loader.calssification_to_edge_to_tag[classification]
            [feature_matrix, tags_vector, node_to_zscoringfeatures] = features_matrix.build_matrix_with_tags_edges \
                (gnx, map_fetures, edges_to_tags, zscoring=True)
            tags_vector = np.squeeze(np.asarray(tags_vector))
            l = ml.SimpleMachineLearning(feature_matrix, tags_vector)
            if len(set(edges_to_tags.values())) != 2:
                run_multiclass_machine_learning(classification, features_importance_dict, l, ml_algos, edges_to_tags,
                                                node_to_zscoringfeatures, number_of_learning_for_mean, result_path)

            else:
                run_binary_machine_learning(classification, features_importance_dict, l, ml_algos, edges_to_tags,
                                            node_to_zscoringfeatures, number_of_learning_for_mean, result_path)

    else:
        for classification in classifications:
            vertex_to_tags = tags_loader.calssification_to_vertex_to_tag[classification]
            [feature_matrix, tags_vector, node_to_zscoringfeatures] = features_matrix.build_matrix_with_tags\
                                                                            (gnx, map_fetures, vertex_to_tags, zscoring=True)
            tags_vector = np.squeeze(np.asarray(tags_vector))
            l = ml.SimpleMachineLearning(feature_matrix, tags_vector)
            if len(set(vertex_to_tags.values())) != 2:
                run_multiclass_machine_learning(classification, features_importance_dict, l, ml_algos,vertex_to_tags,
                                                node_to_zscoringfeatures, number_of_learning_for_mean, result_path)

            else:
                run_binary_machine_learning(classification, features_importance_dict, l, ml_algos, vertex_to_tags,
                                            node_to_zscoringfeatures, number_of_learning_for_mean, result_path)


def run_multiclass_machine_learning(classification, features_importance_dict, l, ml_algos,vertex_to_tags,
                                    node_to_zscoringfeatures, number_of_learning_for_mean, result_path):
    confusion_matrix_file_name = result_path + classification + '_confusion_matrix.txt'
    confusion_matrix_file = open(confusion_matrix_file_name, 'a')
    features_importance_file_name = result_path + 'features_importance.csv'
    features_importance_file = open(features_importance_file_name, 'w')
    for algo in ml_algos:
        print algo
        sum_confusion_matrix_test = 0
        sum_feature_importance = 0
        for i in range(int(number_of_learning_for_mean)):
            cls = l.implementLearningMethod(algo)
            if i < 2:
                coloring_file_name = result_path + algo +'_coloring.txt'
                l.write_coloring_file(node_to_zscoringfeatures, vertex_to_tags, coloring_file_name)
            # if (algo == 'RF'):
            #     sum_feature_importance += cls.feature_importances_
            #     print len(cls.feature_importances_)
            #     print cls.feature_importances_
            cm = l.evaluate_confusion_metric_test()
            sum_confusion_matrix_test += cm
        confusion_matrix_file.writelines(algo + ',' + str(sum_confusion_matrix_test))
        plot_file_name = result_path + '//' + algo + '_confusion_matrix.png'
        l.plot_confusion_matrix(sum_confusion_matrix_test, ['0', '1', '2', '3', '4', '5', '6'], True,
                                title='Confusion Matrix', plot_file_name=plot_file_name)

        # if algo == 'RF':
        #     for fi in features_importance_dict:
        #         feature_importance_value = sum_feature_importance[fi] / number_of_learning_for_mean
        #         features_importance_file.writelines(
        #             features_importance_dict[fi] + ',' + str(feature_importance_value) + '\n')
    features_importance_file.close()
    confusion_matrix_file.close()


def run_binary_machine_learning(classification, features_importance_dict, l, ml_algos, vertex_to_tags,
                                node_to_zscoringfeatures, number_of_learning_for_mean, result_path):
    output_file_name = result_path + classification + '_auc.csv'
    auc_file = open(output_file_name, 'a')
    features_importance_file_name = result_path + classification + '_features_importance.csv'
    features_importance_file = open(features_importance_file_name, 'w')
    for algo in ml_algos:
        print algo
        sum_auc_test = 0
        sum_auc_train = 0
        sum_feature_importance = 0
        for i in range(int(number_of_learning_for_mean)):
            cls = l.implementLearningMethod(algo)
            # if i < 2:
            #     coloring_file_name = result_path + algo +'_coloring.txt'
            #     l.write_coloring_file(node_to_zscoringfeatures, vertex_to_tags, coloring_file_name)
            # if (algo == 'RF'):
            #     sum_feature_importance += cls.feature_importances_
            #     print len(cls.feature_importances_)
            #     print cls.feature_importances_
            auc_test = l.evaluate_AUC_test()
            print 'auc_test', auc_test
            sum_auc_test += auc_test
            auc_train = l.evaluate_AUC_train()
            print 'auc_train', auc_train
            sum_auc_train += auc_train
        auc_file.writelines(algo + ',' + str(sum_auc_test / number_of_learning_for_mean) + '\n')
        print 'mean_feature_importance', sum_feature_importance / number_of_learning_for_mean
        print 'mean_auc_test', sum_auc_test / number_of_learning_for_mean
        print 'mean_auc_train', sum_auc_train / number_of_learning_for_mean
        # if algo == 'RF':
        #     for fi in features_importance_dict:
        #         feature_importance_value = sum_feature_importance[fi] / number_of_learning_for_mean
        #         features_importance_file.writelines(
        #             features_importance_dict[fi] + ',' + str(feature_importance_value) + '\n')
    features_importance_file.close()
    auc_file.close()


def deepLearning(gnx, map_fetures, number_of_learning_for_mean, classifications,tags_loader, result_path,edges=False):
    from learning import deep_learning as deep
    if(edges):
        for classification in classifications:
            edge_to_tags = tags_loader.calssification_to_edge_to_tag[classification]
            result = features_matrix.build_matrix_with_tags(gnx, map_fetures, edge_to_tags, zscoring=True)
            feature_matrix = result[0]
            tags_vector = np.squeeze(np.asarray(result[1]))
            deepL = deep.DeepLearning(feature_matrix, tags_vector)

            if len(set(edge_to_tags.values())) != 2:
                run_multiclass_deep_learning(classification, deepL, number_of_learning_for_mean, result_path)
            else:
                run_binary_deep_learning(classification, deepL, number_of_learning_for_mean, result_path)
    else:
        for classification in classifications:

            vertex_to_tags = tags_loader.calssification_to_vertex_to_tag[classification]
            result = features_matrix.build_matrix_with_tags(gnx, map_fetures, vertex_to_tags, zscoring=True)
            feature_matrix = result[0]
            tags_vector = np.squeeze(np.asarray(result[1]))
            deepL = deep.DeepLearning(feature_matrix, tags_vector)

            if len(set(vertex_to_tags.values())) != 2:
                run_multiclass_deep_learning(classification, deepL, number_of_learning_for_mean, result_path)
            else:
                run_binary_deep_learning(classification, deepL, number_of_learning_for_mean, result_path)


def run_multiclass_deep_learning(classification, deepL, number_of_learning_for_mean, result_path):
    confusion_matrix_file = result_path + classification + '_confusion_matrix.txt'
    sum_confusion_matrix_test = 0
    for i in range(int(number_of_learning_for_mean)):
        cls = deepL.runNetwork(0.2, output_activation='softmax', output_size=7)
        cm = deepL.evaluate_confusion_metric_test()
        sum_confusion_matrix_test += cm
    confusion_matrix_file.writelines('deep,' + str(sum_confusion_matrix_test))
    plot_file_name = result_path + '//deep_confusion_matrix.png'
    deepL.plot_confusion_matrix(sum_confusion_matrix_test, ['0', '1', '2', '3', '4', '5', '6'], True,
                                title='Confusion Matrix', plot_file_name=plot_file_name)
    confusion_matrix_file.close()


def run_binary_deep_learning(classification, deepL, number_of_learning_for_mean, result_path):
    sum_auc_test = 0
    sum_auc_train = 0
    sum_f1_test = 0
    output_file_name = result_path + classification + '_auc.csv'
    auc_file = open(output_file_name, 'a')
    for i in range(int(number_of_learning_for_mean)):
        cls = deepL.runNetwork(0.2)
        auc_test = deepL.evaluate_AUC_test()
        print 'auc_test', auc_test
        sum_auc_test += auc_test
        auc_train = deepL.evaluate_AUC_train()
        print 'auc_train', auc_train
        sum_auc_train += auc_train
        f1_score = deepL.evaluate_f1_score()
        print 'f1_score', f1_score
        sum_f1_test += f1_score
    auc_file.writelines('deep ,' + str(sum_auc_test / number_of_learning_for_mean) + '\n')
    auc_file.writelines('deep f1,' + str(sum_f1_test/number_of_learning_for_mean) + '\n')
    print 'mean_auc_test', sum_auc_test / number_of_learning_for_mean
    print 'mean_auc_train', sum_auc_train / number_of_learning_for_mean
    print 'mean_f1_test', sum_f1_test/number_of_learning_for_mean
    auc_file.close()

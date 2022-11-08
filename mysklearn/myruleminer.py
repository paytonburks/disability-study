import copy
from tabulate import tabulate

class MyAssociationRuleMiner:
    """Represents an association rule miner.

    Attributes:
        minsup(float): The minimum support value to use when computing supported itemsets
        minconf(float): The minimum confidence value to use when generating rules
        X_train(list of list of obj): The list of training instances (samples)
                The shape of X_train is (n_train_samples, n_features)
        rules(list of dict): The generated rules

    Notes:
        Implements the apriori algorithm
        Terminology: instance = sample = row and attribute = feature = column
    """
    def __init__(self, minsup=0.25, minconf=0.8):
        """Initializer for MyAssociationRuleMiner.

        Args:
            minsup(float): The minimum support value to use when computing supported itemsets
                (0.25 if a value is not provided and the default minsup should be used)
            minconf(float): The minimum confidence value to use when generating rules
                (0.8 if a value is not provided and the default minconf should be used)
        """
        self.minsup = minsup
        self.minconf = minconf
        self.X_train = None

        # IF interviewed_well=False THEN tweets=no
        # rule1 = {"lhs": ["interviewed_well=False"], "rhs": ["tweets=no"], "support": 0.69 "confidence": 0.69, "lift": 0.69}
        self.rules = None

    def fit(self, X_train):
        """Fits an association rule miner to X_train using the Apriori algorithm.

        Args:
            X_train(list of list of obj): The list of training instances (samples)
                The shape of X_train is (n_train_samples, n_features)

        Notes:
            Store the list of generated association rules in the rules attribute
            If X_train represents a non-market basket analysis dataset, then:
                Attribute labels should be prepended to attribute values in X_train
                    before fit() is called (e.g. "att=val", ...).
                Make sure a rule does not include the same attribute more than once
        """
        def compute_unique_values(table):
            unique = set()
            for row in table:
                for value in row: 
                    unique.add(value)
            return sorted(list(unique))

        def compute_k_minus_1_subsets(itemset):
            subsets = []
            for i in range(len(itemset)):
                subsets.append(itemset[:i] + itemset[i + 1:])
            return subsets                    

        def generate_apriori_rules(supported_itemsets):
            def numcheck(l, r):
                num = 0
                for instance in self.X_train:
                    Lresult =  all(elem in instance for elem in l)
                    if Lresult:
                        Rresult =  all(elem in instance for elem in r)
                        if Rresult:
                            num+=1
                
                return num

            def denomcheck(l):
                denom = 0
                for instance in self.X_train:
                    Lresult =  all(elem in instance for elem in l)
                    if Lresult:
                        denom+=1
            
                return denom

            def calculate_rstats(l, r):
                n_left = 0
                n_right = 0
                n_both = 0
                n_tot = len(self.X_train)
            
                for instance in self.X_train:
                    Lresult =  all(elem in instance for elem in l)
                    if Lresult:
                        n_left+=1
                        Rresult =  all(elem in instance for elem in r)
                        if Rresult:
                            n_right+=1
                            n_both+=1
                    else:
                        Rresult =  all(elem in instance for elem in r)
                        if Rresult:
                            n_right+=1

                # sup
                sup = n_both/n_tot
                # conf
                conf = n_both/n_left
                # lift
                lift = (n_both/n_tot) / ( (n_left/n_tot) * (n_right/n_tot) )

                return sup, conf, lift

            rules = []
            # for each itemset S in supported_itemsets
            for itemset in supported_itemsets:
                temp = combs(itemset)
                rhs_poss = []
                for item in temp:
                    if len(item) > 0 and len(item) < len(itemset):
                        rhs_poss.append(item)
                
                lhs_poss = []
                for r in rhs_poss:
                    ins = []
                    for item in itemset:
                        if item not in r:
                            ins.append(item)
                    lhs_poss.append(ins)

                # check confidence >= minconf => append to rules
                conf_pass = []
            
                for n in range(len(rhs_poss)):
                    num = numcheck(rhs_poss[n], lhs_poss[n])
                    denom = denomcheck(lhs_poss[n])

                    if denom == 0:
                        pass
                    else:
                        conf = num/denom
                        if conf >= self.minconf:
                            rule_sup, rule_conf, rule_lift = calculate_rstats(lhs_poss[n], rhs_poss[n])
                            conf_pass.append({"lhs": lhs_poss[n], "rhs": rhs_poss[n], "support": round(rule_sup, 2), "confidence": round(rule_conf, 2), "lift": round(rule_lift, 2)})
                if conf_pass != []:
                    for item in conf_pass:
                        rules.append(item)

            return rules 
        
        def combs(a):
            if len(a) == 0:
                return [[]]
            cs = []
            for c in combs(a[1:]):
                cs += [c, c+[a[0]]]
            return cs

        def check_support(item):
            curr = copy.deepcopy(self.X_train)
            for a in item:
                i=0
                while i < len(curr):
                    if a not in curr[i]:
                        del curr[i]
                        i-=1
                    i+=1
            return len(curr)

        def generate_ck(Lkminus1, k):
            # singleton exception
            ck = []
            if ',' not in str(Lkminus1[0]):
                temp = combs(Lkminus1)
                for item in temp:
                    if len(item) == k:
                        item.sort()
                        ck.append(item)
            else:
                ck = []
                for item in Lkminus1:
                    ind = Lkminus1.index(item)

                    left_elements = item[:-1]
                    right_element = item[-1]

                    for i in range(len(Lkminus1)):
                        if i == ind:
                            pass
                        else:
                            les = Lkminus1[i][:-1]
                            re = Lkminus1[i][-1]

                            les.sort()
                            left_elements.sort()
                            if les == left_elements:
                                    les.append(right_element)
                                    les.append(re)
                                    les.sort()
                                    if les not in ck:
                                        ck.append(les)

            return ck

        def apriori(table, minsup, minconf):
            supported_itemsets = []
            # generate L1 supported itemsets of cardinality 1
            I = compute_unique_values(table)

            # check support of singletons in L1
            singleton_percents = []
            # generate base percents for each singleton
            for item in I:
                singleton_percents.append(0)

            # iterate through table and get support
            for i in range(len(I)):
                for instance in table:
                    if I[i] in instance:
                        singleton_percents[i] += 1

            for i in range(len(singleton_percents)):
                singleton_percents[i] = singleton_percents[i]/len(table)

            i = 0
            while i < len(singleton_percents):
                if singleton_percents[i] < minsup:
                    del singleton_percents[i]
                    del I[i]
                    i-=1
                i+=1

            # initialize lk
            k = 2
            Lkminus1 = []
            for item in I:
                Lkminus1.append(item)
            
            # while loop... while(Lkminus1 is not empty)
            while len(Lkminus1) != 0:
                ck = generate_ck(Lkminus1, k)
                # ck established, start pruning
                n = 0
                while n < len(ck):
                    # check if items in combos are in Lkminus1
                    seperate_combos = compute_k_minus_1_subsets(ck[n])
                    for combo in seperate_combos:
                        combo.sort()
                        if k == 2:
                            if combo[0] not in Lkminus1:
                                del ck[n]
                                n-=1
                                break

                        else:
                            if combo not in Lkminus1:
                                del ck[n]
                                n-=1
                                break
                    n+=1

                # check if each item currently in ck has minsup
                minsup_counts = []
                for item in ck:
                    minsup_counts.append(0)
                for q in range(len(ck)):
                    num = check_support(ck[q])
                    minsup_counts[q]+=num
                for i in range(len(minsup_counts)):
                    minsup_counts[i] /= len(self.X_train)

                i = 0
                while i < len(minsup_counts):
                    if minsup_counts[i] < self.minsup:
                        del ck[i]
                        del minsup_counts[i]
                        i-=1
                    i+=1

                # loop finished, store ck, increase k, repeat
                ck.sort()
                ('ck after sort:', ck)
                if len(ck) > 0:
                    for item in ck:
                        supported_itemsets.append(item)
                Lkminus1 = ck
                k+=1

            rules = generate_apriori_rules(supported_itemsets)
            return rules 

        self.X_train = X_train
        self.rules = apriori(X_train, self.minsup, self.minconf)

    def print_association_rules(self):
        """Prints the association rules in the format "IF val AND ... THEN val AND...", one rule on each line.

        Notes:
            Each rule's output should include an identifying number, the rule, the rule's support,
            the rule's confidence, and the rule's lift
            Consider using the tabulate library to help with this: https://pypi.org/project/tabulate/
        """
        strings = []
        for rule in self.rules:
            state = "IF "
            for i in range(len(rule['lhs'])):
                if i+1 < len(rule['lhs']):
                    state+= str(rule['lhs'][i]) + " AND "
                else:
                    state+= str(rule['lhs'][i])
            state+= " THEN "
            for n in range(len(rule['rhs'])):
                if n+1 < len(rule['rhs']):
                    state+= str(rule['rhs'][n]) + " AND "
                else:
                    state+= str(rule['rhs'][n])
            strings.append(state)

        table = []
        for i in range(len(strings)):
            table.append([i+1, strings[i], self.rules[i]['support'], self.rules[i]['confidence'], self.rules[i]['lift']])

        print(tabulate(table, headers=['#', 'rule', 'support', 'confidence', 'lift']))

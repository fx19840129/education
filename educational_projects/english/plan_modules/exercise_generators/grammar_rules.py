#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语法规则和单词变形模块
提供各种语法变形规则的统一接口
"""

from typing import Dict, List, Tuple


class GrammarRules:
    """语法规则处理类"""
    
    def __init__(self):
        # 不规则动词表
        self.irregular_verbs = {
            'go': {'past': 'went', 'past_participle': 'gone', 'third_person': 'goes'},
            'have': {'past': 'had', 'past_participle': 'had', 'third_person': 'has'},
            'do': {'past': 'did', 'past_participle': 'done', 'third_person': 'does'},
            'make': {'past': 'made', 'past_participle': 'made', 'third_person': 'makes'},
            'take': {'past': 'took', 'past_participle': 'taken', 'third_person': 'takes'},
            'see': {'past': 'saw', 'past_participle': 'seen', 'third_person': 'sees'},
            'come': {'past': 'came', 'past_participle': 'come', 'third_person': 'comes'},
            'give': {'past': 'gave', 'past_participle': 'given', 'third_person': 'gives'},
            'write': {'past': 'wrote', 'past_participle': 'written', 'third_person': 'writes'},
            'read': {'past': 'read', 'past_participle': 'read', 'third_person': 'reads'},
            'say': {'past': 'said', 'past_participle': 'said', 'third_person': 'says'},
            'get': {'past': 'got', 'past_participle': 'gotten', 'third_person': 'gets'},
            'think': {'past': 'thought', 'past_participle': 'thought', 'third_person': 'thinks'},
            'know': {'past': 'knew', 'past_participle': 'known', 'third_person': 'knows'},
            'find': {'past': 'found', 'past_participle': 'found', 'third_person': 'finds'},
            'tell': {'past': 'told', 'past_participle': 'told', 'third_person': 'tells'},
            'become': {'past': 'became', 'past_participle': 'become', 'third_person': 'becomes'},
            'leave': {'past': 'left', 'past_participle': 'left', 'third_person': 'leaves'},
            'feel': {'past': 'felt', 'past_participle': 'felt', 'third_person': 'feels'},
            'bring': {'past': 'brought', 'past_participle': 'brought', 'third_person': 'brings'},
        }
        
        # 不规则形容词比较级和最高级
        self.irregular_adjectives = {
            'good': {'comparative': 'better', 'superlative': 'best'},
            'bad': {'comparative': 'worse', 'superlative': 'worst'},
            'far': {'comparative': 'farther', 'superlative': 'farthest'},
            'little': {'comparative': 'less', 'superlative': 'least'},
            'many': {'comparative': 'more', 'superlative': 'most'},
            'much': {'comparative': 'more', 'superlative': 'most'},
        }
        
        # 不规则名词复数
        self.irregular_nouns = {
            'child': 'children',
            'man': 'men',
            'woman': 'women',
            'foot': 'feet',
            'tooth': 'teeth',
            'mouse': 'mice',
            'goose': 'geese',
            'sheep': 'sheep',
            'fish': 'fish',
            'deer': 'deer',
        }
    
    # 动词变形方法
    def get_third_person_form(self, verb: str) -> str:
        """获取动词第三人称单数形式"""
        if verb in self.irregular_verbs:
            return self.irregular_verbs[verb]['third_person']
        elif verb.endswith(('s', 'x', 'ch', 'sh', 'o')):
            return f"{verb}es"
        elif verb.endswith('y') and len(verb) > 1 and verb[-2] not in 'aeiou':
            return f"{verb[:-1]}ies"
        else:
            return f"{verb}s"
    
    def get_third_person_rule(self, verb: str) -> str:
        """获取第三人称单数变化规则"""
        if verb in self.irregular_verbs:
            return f"不规则变化：{verb} → {self.irregular_verbs[verb]['third_person']}"
        elif verb.endswith(('s', 'x', 'ch', 'sh', 'o')):
            return f"以s, x, ch, sh, o结尾加-es"
        elif verb.endswith('y') and len(verb) > 1 and verb[-2] not in 'aeiou':
            return f"以辅音+y结尾，变y为i加-es"
        else:
            return f"一般情况加-s"
    
    def get_past_form(self, verb: str) -> str:
        """获取动词过去式"""
        if verb in self.irregular_verbs:
            return self.irregular_verbs[verb]['past']
        elif verb.endswith('e'):
            return f"{verb}d"
        elif verb.endswith('y') and len(verb) > 1 and verb[-2] not in 'aeiou':
            return f"{verb[:-1]}ied"
        elif self._is_cvc_pattern(verb):
            return f"{verb}{verb[-1]}ed"
        else:
            return f"{verb}ed"
    
    def get_past_rule(self, verb: str) -> str:
        """获取过去式变化规则"""
        if verb in self.irregular_verbs:
            return f"不规则变化：{verb} → {self.irregular_verbs[verb]['past']}"
        elif verb.endswith('e'):
            return f"以e结尾的动词，过去式加-d"
        elif verb.endswith('y') and len(verb) > 1 and verb[-2] not in 'aeiou':
            return f"以辅音+y结尾的动词，变y为i加-ed"
        elif self._is_cvc_pattern(verb):
            return f"重读闭音节动词，双写末尾辅音加-ed"
        else:
            return f"一般动词，过去式加-ed"
    
    def get_ing_form(self, verb: str) -> str:
        """获取动词-ing形式"""
        if verb.endswith('e') and len(verb) > 2:
            return f"{verb[:-1]}ing"
        elif self._is_cvc_pattern(verb):
            return f"{verb}{verb[-1]}ing"
        else:
            return f"{verb}ing"
    
    def get_ing_rule(self, verb: str) -> str:
        """获取-ing变化规则"""
        if verb.endswith('e') and len(verb) > 2:
            return f"以e结尾的动词，去e加-ing"
        elif self._is_cvc_pattern(verb):
            return f"重读闭音节动词，双写末尾辅音加-ing"
        else:
            return f"一般动词，直接加-ing"
    
    def get_past_participle(self, verb: str) -> str:
        """获取过去分词"""
        if verb in self.irregular_verbs:
            return self.irregular_verbs[verb]['past_participle']
        else:
            return self.get_past_form(verb)
    
    def get_past_participle_rule(self, verb: str) -> str:
        """获取过去分词变化规则"""
        if verb in self.irregular_verbs:
            return f"不规则变化：{verb} → {self.irregular_verbs[verb]['past_participle']}"
        else:
            return self.get_past_rule(verb)
    
    # 名词变形方法
    def get_plural_form(self, noun: str) -> str:
        """获取名词复数形式"""
        if noun in self.irregular_nouns:
            return self.irregular_nouns[noun]
        elif noun.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return f"{noun}es"
        elif noun.endswith('y') and len(noun) > 1 and noun[-2] not in 'aeiou':
            return f"{noun[:-1]}ies"
        elif noun.endswith('f'):
            return f"{noun[:-1]}ves"
        elif noun.endswith('fe'):
            return f"{noun[:-2]}ves"
        elif noun.endswith('o') and len(noun) > 1 and noun[-2] not in 'aeiou':
            return f"{noun}es"
        else:
            return f"{noun}s"
    
    def get_plural_rule(self, noun: str) -> str:
        """获取名词复数变化规则"""
        if noun in self.irregular_nouns:
            return f"不规则变化：{noun} → {self.irregular_nouns[noun]}"
        elif noun.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return f"以s, sh, ch, x, z结尾的名词，复数加-es"
        elif noun.endswith('y') and len(noun) > 1 and noun[-2] not in 'aeiou':
            return f"以辅音字母+y结尾的名词，变y为i再加-es"
        elif noun.endswith('f'):
            return f"以f结尾的名词，变f为v再加-es"
        elif noun.endswith('fe'):
            return f"以fe结尾的名词，变fe为v再加-es"
        elif noun.endswith('o') and len(noun) > 1 and noun[-2] not in 'aeiou':
            return f"以辅音字母+o结尾的名词，复数加-es"
        else:
            return f"一般名词复数直接加-s"
    
    # 形容词变形方法
    def get_comparative_form(self, adjective: str) -> str:
        """获取形容词比较级形式"""
        if adjective in self.irregular_adjectives:
            return self.irregular_adjectives[adjective]['comparative']
        elif len(adjective) <= 4:  # 单音节词
            if adjective.endswith('e'):
                return f"{adjective}r"
            elif adjective.endswith('y') and len(adjective) > 1 and adjective[-2] not in 'aeiou':
                return f"{adjective[:-1]}ier"
            elif self._is_cvc_pattern(adjective):
                return f"{adjective}{adjective[-1]}er"
            else:
                return f"{adjective}er"
        else:  # 多音节词
            return f"more {adjective}"
    
    def get_comparative_rule(self, adjective: str) -> str:
        """获取形容词比较级变化规则"""
        if adjective in self.irregular_adjectives:
            return f"不规则变化：{adjective} → {self.irregular_adjectives[adjective]['comparative']}"
        elif len(adjective) <= 4:
            if adjective.endswith('e'):
                return "以e结尾的形容词，比较级加-r"
            elif adjective.endswith('y') and len(adjective) > 1 and adjective[-2] not in 'aeiou':
                return "以辅音+y结尾的形容词，变y为i加-er"
            elif self._is_cvc_pattern(adjective):
                return "重读闭音节词，双写末尾辅音加-er"
            else:
                return "单音节形容词，比较级加-er"
        else:
            return "多音节形容词，比较级用more + 形容词"
    
    def get_superlative_form(self, adjective: str) -> str:
        """获取形容词最高级形式"""
        if adjective in self.irregular_adjectives:
            return self.irregular_adjectives[adjective]['superlative']
        elif len(adjective) <= 4:
            if adjective.endswith('e'):
                return f"{adjective}st"
            elif adjective.endswith('y') and len(adjective) > 1 and adjective[-2] not in 'aeiou':
                return f"{adjective[:-1]}iest"
            elif self._is_cvc_pattern(adjective):
                return f"{adjective}{adjective[-1]}est"
            else:
                return f"{adjective}est"
        else:
            return f"most {adjective}"
    
    # 其他语法方法
    def get_random_modal_verb(self) -> str:
        """获取随机情态动词"""
        import random
        modal_verbs = ['can', 'could', 'may', 'might', 'must', 'should', 'will', 'would']
        return random.choice(modal_verbs)
    
    def get_modal_meaning(self, modal_verb: str) -> str:
        """获取情态动词英文含义"""
        meanings = {
            'can': 'ability',
            'could': 'possibility',
            'may': 'permission',
            'might': 'possibility',
            'must': 'necessity',
            'should': 'advice',
            'will': 'future',
            'would': 'conditional'
        }
        return meanings.get(modal_verb, 'modal verb')
    
    def get_modal_meaning_chinese(self, modal_verb: str) -> str:
        """获取情态动词中文含义"""
        meanings = {
            'can': '能够',
            'could': '可能',
            'may': '可以',
            'might': '可能',
            'must': '必须',
            'should': '应该',
            'will': '将要',
            'would': '会'
        }
        return meanings.get(modal_verb, '能够')
    
    def get_verb_type(self, verb: str) -> str:
        """随机选择动词类型（用于练习题变化）"""
        import random
        return random.choice(["first_person", "third_person"])
    
    # 辅助方法
    def _is_cvc_pattern(self, word: str) -> bool:
        """判断是否为辅音+元音+辅音模式"""
        if len(word) < 3:
            return False
        vowels = 'aeiou'
        return (word[-3] not in vowels and 
                word[-2] in vowels and 
                word[-1] not in vowels and
                word[-1] not in 'wx')  # w,x通常不双写
    
    def is_uncountable_noun(self, noun: str) -> bool:
        """判断是否为不可数名词"""
        uncountable_nouns = {
            'water', 'milk', 'juice', 'coffee', 'tea', 'oil', 'air', 
            'music', 'information', 'news', 'advice', 'money', 'time',
            'weather', 'homework', 'work', 'furniture', 'equipment'
        }
        return noun.lower() in uncountable_nouns

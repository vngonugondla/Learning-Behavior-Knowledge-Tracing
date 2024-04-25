import heapq

class PriorityQueue:
    def __init__(self, topics):
        self.heap = [(0, topic) for topic in topics] #["Frequency Analysis", "Filter Design", "Modulation Techniques"]
        self.topic_mapping = {}
        count = 0
        for topic in topics:
            self.topic_mapping[topic] = count
            count+=1

    """def push(self, topic, topic_accuracy):
        if topic in self.topic_mapping:
            self.heap[0] = (topic_accuracy, topic)
        else:
            self.heap.insert(0,(topic_accuracy, topic))
            self.topic_mapping[topic] = len(self.heap) - 1
    """
    def push(self, topic, topic_accuracy):
        inserted = False
        self.heap.pop(self.topic_mapping[topic])

        for ind, tup in enumerate(self.heap):
            if topic_accuracy <= tup[0]:
                self.heap.insert(ind, (topic_accuracy, topic))
                inserted = True
                break

        if not inserted:
            self.heap.append((topic_accuracy, topic))


        count = 0
        for tup in self.heap:
            topic = tup[1]
            self.topic_mapping[topic] = count
            count+=1
        


        """if topic in self.topic_mapping:
            self.heap[0] = (topic_accuracy, topic)
        else:
            self.heap.insert(0,(topic_accuracy, topic))
            self.topic_mapping[topic] = len(self.heap) - 1
            """
    


    def pop(self):
        if self.is_empty():
            return None
        removed = self.heap[0]
        self.heap.pop(0)
        for topic in self.topic_mapping:
            self.topic_mapping[topic] -= 1
        return removed


    def is_empty(self):
        return len(self.heap) == 0


class prev:
    _instance=None
    def __new__(cls):
         if cls._instance is None:
            cls._instance = super(prev, cls).__new__(cls)
            cls._instance.prevData = None
            cls._instance.prevEntity = None
            cls._instance.prevIntent = None            
            return cls._instance
prevObj = prev()
def setValues(prevI,prevE,prevD):
    prevObj.prevIntent=prevI
    prevObj.prevEntity=prevE
    prevObj.prevData=prevD
    
def repeat():
    from app.services.nlp import dynamicActionMapping
    return dynamicActionMapping(prevObj.prevIntent,prevObj.prevEntity,prevObj.prevData)
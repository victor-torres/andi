def as_class_names(cls_or_collection):
    try:
        return [cls.__name__ for cls in cls_or_collection]
    except:
        try:
            return cls_or_collection.__name__
        except:
            return str(cls_or_collection)


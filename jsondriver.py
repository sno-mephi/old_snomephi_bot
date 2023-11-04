import json
from typing import List, Dict, Union, Any
import random
import string

NOT_FOUND = object()


class AsyncJsonCollection:
    """
    Asynchronous collection model based on json module.
    """

    async def query_fulfills(obj, query):
        if isinstance(query, int) or isinstance(query, float) or isinstance(query, str) or isinstance(query, bool):
            return True if obj == query else False
        elif '$exists' in query:
            result = True if obj is not NOT_FOUND else False
            if query['$exists']:
                return result
            else:
                return not result
        elif '$ne' in query:
            return True if obj != query['$ne'] else False
        else:
            return True if obj == query else False
    

    async def perform_action(self, _id: Union[str, int], action: Union[str, None], _action: Union[Dict[str, Any], Any]) -> bool:
        if action == '$set':
            for field in _action[action]:
                if '.' in field:
                    _field, index = field.split('.')
                    if type(self.__json[_id][_field]) is list:
                        self.__json[_id][_field][int(index)] = _action[action][field]
                    elif type(self.__json[_id][_field]) is dict:
                        self.__json[_id][_field][index] = _action[action][field]
                else:
                    self.__json[_id][field] = _action[action][field]
        elif action == '$unset':
            for field in _action[action]:
                if '.' in field:
                    _field, index = field.split('.')
                    if type(self.__json[_id][_field]) is list:
                        self.__json[_id][_field].pop(int(index), NOT_FOUND)
                    elif type(self.__json[_id][_field]) is dict:
                        self.__json[_id][_field].pop(index, NOT_FOUND)
                else:
                    self.__json[_id].pop(field, NOT_FOUND)
        else:
            self.__json[_id] = _action
            return True
        return False


    def __init__(self, file_path: str = "", json_object: Union[Dict, None] = None):
        if json_object is None:
            self.__file_path = file_path
            try:
                with open(file_path, 'r') as file:
                    self.__json = json.load(file)
            except FileNotFoundError:
                file = open(file_path, 'w+')
                file.write('{}')
                file.close()
                self.__init__(file_path)
        else:
            self.__json = json_object
    

    async def reload(self) -> None:
        """
        Destroys current version of the collection and replaces it with the one stored on the disk.
        """
        try:
            with open(self.__file_path, 'r') as file:
                self.__json = json.load(file)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    

    async def save(self) -> None:
        """
        Update version of the collection stored on the disk.
        """
        try:
            file = open(self.__file_path, 'w')
            json.dump(self.__json, file, indent=4)
            file.close()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}


    async def find(self, _format: Dict = {}):
        """
        Iterates over the collection and returns generator of objects, which satisfy _format.

        Arguments:
            _format -- resembles objects which need to be returned

        _format structure: {'field_name': query}.
        
        Possible queries:
            {'$exists': True|False} -- checks whether the field is present or not
             {'$ne': Value} -- checks whether the field's corresponding value is not equal to Value
            Value -- checks whether the field's corresponding value equals to Value
             {'$first|last': True|False} -- checks whether the object is first or last in the collection
        
        '$or' pre-query allows to use logical or to several checks
        """
        for _id in (self.__json if type(self.__json) is dict else range(len(self.__json))):
            verified = True
            for field in _format:
                if field in ('$first', '$last'):
                    verified = (_id == list(self.__json.keys())[0 if field == '$first' else -1])
                    if not _format[field]:
                        verified = not verified
                elif field == '$or':
                    temp_verified = False
                    for real_field in _format[field]:
                        temp_verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(real_field, NOT_FOUND), _format[field][real_field])
                        if temp_verified:
                            break
                    verified = temp_verified
                else:
                    verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(field, NOT_FOUND), _format[field])
                if not verified:
                    break
            if verified:
                yield self.__json[_id]
    

    async def find_one(self, _format: Dict = {}) -> Union[Dict, None]:
        """
        Iterates over the collection and returns first object, which satisfies _format.
        If none are found, then None is returned.

        Arguments:
            _format -- resembles object that needs to be returned

        _format structure: {'field_name': query}.
        
        Possible queries:
            {'$exists': True|False} -- checks whether the field is present or not
             {'$ne': Value} -- checks whether the field's corresponding value is not equal to Value
            Value -- checks whether the field's corresponding value equals to Value
             {'$first|last': True|False} -- checks whether the object is first or last in the collection

        '$or' pre-query allows to use logical or to several checks
        """
        for _id in (self.__json if type(self.__json) is dict else range(len(self.__json))):
            verified = True
            for field in _format:
                if field in ('$first', '$last'):
                    verified = (_id == list(self.__json.keys())[0 if field == '$first' else -1])
                    if not _format[field]:
                        verified = not verified
                elif field == '$or':
                    temp_verified = False
                    for real_field in _format[field]:
                        temp_verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(real_field, NOT_FOUND), _format[field][real_field])
                        if temp_verified:
                            break
                    verified = temp_verified
                else:
                    verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(field, NOT_FOUND), _format[field])
                if not verified:
                    break
            if verified:
                return self.__json[_id]
        return None
    

    async def get(self, _id: str) -> Union[Dict, None]:
        """
        Returns object with correspondning _id.

        Arguments:
            _id -- id of object to return
        """
        if self.__json.get(_id, NOT_FOUND) is not NOT_FOUND:
            return self.__json[_id]
        else:
            return None
    

    async def delete_one(self, _format: Dict = {}) -> Union[Dict, None]:
        """
        Iterates over the collection and deletes first object, which satisfies _format.
        The deleted object is returned. If none are deleted, then None is returned.

        Arguments:
            _format -- resembles object that needs to be deleted

        _format structure: {'field_name': query}.
        
        Possible queries:
            {'$exists': True|False} -- checks whether the field is present or not
             {'$ne': Value} -- checks whether the field's corresponding value is not equal to Value
            Value -- checks whether the field's corresponding value equals to Value
             {'$first|last': True|False} -- checks whether the object is first or last in the collection
        
        '$or' pre-query allows to use logical or to several checks
        """
        for _id in (self.__json if type(self.__json) is dict else range(len(self.__json))):
            verified = True
            for field in _format:
                if field in ('$first', '$last'):
                    verified = (_id == list(self.__json.keys())[0 if field == '$first' else -1])
                    if not _format[field]:
                        verified = not verified
                elif field == '$or':
                    temp_verified = False
                    for real_field in _format[field]:
                        temp_verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(real_field, NOT_FOUND), _format[field][real_field])
                        if temp_verified:
                            break
                    verified = temp_verified
                else:
                    verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(field, NOT_FOUND), _format[field])
                if not verified:
                    break
            if verified:
                return self.__json.pop(_id)
        return None
    
    
    async def pop(self, _id: str) -> Union[Dict, None]:
        """
        Deletes object with correspondning _id. Returns deleted object. If none are deleted, then None is returned

        Arguments:
            _id -- id of object to return
        """
        return self.__json.pop(_id, None)
    

    async def _id(self, obj: Dict) -> Union[str, None]:
        """
        Finds _id of the given object. If several exist, first one found is returned. If none are found, then None is returned.

        Arguments:
            obj -- object whose _id should be returned
        """
        for _id in (self.__json if type(self.__json) is dict else range(len(self.__json))):
            verified = True
            for field in obj:
                verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(field, NOT_FOUND), obj[field])
                if not verified:
                    break
            if verified:
                return _id
        return None
    

    async def insert_one(self, obj: Dict) -> Dict:
        """
        Inserts object into the collection.

        Arguments:
            obj -- object to be added to the collection
        """
        try:
            _id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))
            while self.__json.get(_id, NOT_FOUND) is not NOT_FOUND:
                _id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))
            self.__json.update([(_id, obj)])
            return {'success': True, 'stored_id': _id}
        except Exception as e:
            return {'success': False, 'error': str(e)}


    async def update_one(self, _format: Dict, _action: Dict) -> Dict:
        """
        Iterates over the collection and updates first object, which satisfies _format.

        Arguments:
            _format -- resembles object that needs to be updated
             _action -- updates to be done to objects

        _format structure: {'field_name': query}.
        
        Possible queries:
            {'$exists': True|False} -- checks whether the field is present or not
             {'$ne': Value} -- checks whether the field's corresponding value is not equal to Value
            Value -- checks whether the field's corresponding value equals to Value
             {'$first|last': True|False} -- checks whether the object is first or last in the collection

        '$or' pre-query allows to use logical or to several checks

        _action structure: {'action_name': {'field': Value}}

        Possible actions:
            '$set' -- updates the object with field-Value pairs, ignoring other fields
             '$unset' -- deletes field from the object
            No action -- replaces the object's contents with _action
        """
        try:
            for _id in (self.__json if type(self.__json) is dict else range(len(self.__json))):
                verified = True
                for field in _format:
                    if field in ('$first', '$last'):
                        verified = (_id == list(self.__json.keys())[0 if field == '$first' else -1])
                        if not _format[field]:
                            verified = not verified
                    elif field == '$or':
                        temp_verified = False
                        for real_field in _format[field]:
                            temp_verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(real_field, NOT_FOUND), _format[field][real_field])
                            if temp_verified:
                                break
                        verified = temp_verified
                    else:
                        verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(field, NOT_FOUND), _format[field])
                    if not verified:
                        break
                if verified:
                    break
            for action in _action:
                exit_cycle = await self.perform_action(_id, action, _action)
                if exit_cycle:
                    break
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    

    async def update_many(self, _format: Dict, _action: Dict) -> Dict:
        """
        Iterates over the collection and updates objects, which satisfy _format.

        Arguments:
            _format -- resembles objects which need to be updated
             _action -- updates to be done to objects

        _format structure: {'field_name': query}.
        
        Possible queries:
            '$exists': True|False} -- checks whether the field is present or not
             {'$ne': Value} -- checks whether the field's corresponding value is not equal to Value
            Value -- checks whether the field's corresponding value equals to Value
             {'$first|last': True|False} -- checks whether the object is first or last in the collection

        '$or' pre-query allows to use logical or to several checks

        _action structure: {'action_name': {'field': Value}}

        Possible actions:
            '$set' -- updates the object with field-Value pairs, ignoring other fields
             '$unset' -- deletes field from the object
            No action -- replaces the object's contents with _action
        """
        n = 0
        try:
            for _id in (self.__json if type(self.__json) is dict else range(len(self.__json))):
                verified = True
                for field in _format:
                    if field in ('$first', '$last'):
                        verified = (_id == list(self.__json.keys())[0 if field == '$first' else -1])
                        if not _format[field]:
                            verified = not verified
                    elif field == '$or':
                        temp_verified = False
                        for real_field in _format[field]:
                            temp_verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(real_field, NOT_FOUND), _format[field][real_field])
                            if temp_verified:
                                break
                        verified = temp_verified
                    else:
                        verified = await AsyncJsonCollection.query_fulfills(self.__json[_id].get(field, NOT_FOUND), _format[field])
                    if not verified:
                        break
                if verified:
                    n += 1
                    for action in _action:
                        exit_cycle = await self.perform_action(_id, action, _action)
                        if exit_cycle:
                            break
            return {'success': True, 'updated': n}
        except Exception as e:
            return {'success': False, 'error': str(e)}
